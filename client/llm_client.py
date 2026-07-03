import asyncio
import os
import random
from typing import Any, AsyncGenerator
from google import genai
from google.genai import types
from dotenv import load_dotenv

from client.response import StreamEventType, StreamEvent, TokenUsage, TextDelta

load_dotenv()


class LLMClient:
    def __init__(self) -> None:
        self._client: genai.Client | None = None
        self.min_delay = 0.1
        self.max_delay = 0.3

    def _get_typing_delay(self) -> float:
        """Get random delay between min and max for natural typing"""
        return random.uniform(self.min_delay, self.max_delay)

    def get_client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(
                api_key=os.getenv("GEMINI_API_KEY"),
            )
        return self._client

    async def close(self) -> None:
        self._client = None

    async def chat_completetion(
        self, messages: list[dict[str, Any]], stream: bool = True
    ) -> AsyncGenerator[StreamEvent, None]:
        client = self.get_client()
        model = "gemini-3-flash-preview"

        contents = self._convert_messages_to_gemini_format(messages)

        generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_level="HIGH",
            ),
        )

        if stream:
            async for event in self._stream_response(
                client, model, contents, generate_content_config
            ):
                yield event
        else:
            event = await self._non_stream_response(
                client, model, contents, generate_content_config
            )
            yield event

    def _convert_messages_to_gemini_format(self, messages: list[dict[str, Any]]):
        """Convert OpenAI-style messages to Gemini format"""
        contents = []
        for msg in messages:
            if msg["role"] == "assistant":
                role = "model"
            elif msg["role"] == "system":
                content = f"System instruction: {msg['content']}"
                role = "user"
            else:
                role = "user"

            contents.append(
                types.Content(
                    role=role,
                    parts=[
                        types.Part.from_text(text=msg["content"]),
                    ],
                )
            )
        return contents

    async def _stream_response(
        self, client, model, contents, config
    ) -> AsyncGenerator[StreamEvent, None]:
        """Handle streaming responses - yields chunks and final token usage"""
        try:
            # First, make a non-streaming call to get token usage
            # (This is the only way to get usage from Gemini)

            complete_response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )

            # Extract token usage
            usage_info = self._extract_token_usage(complete_response)
            usage = None
            if usage_info:
                usage = TokenUsage(
                    prompt_tokens=usage_info["prompt_tokens"],
                    completetion_tokens=usage_info["completion_tokens"],
                    cached_tokens=usage_info["cached_tokens"],
                    total_tokens=usage_info["total_tokens"],
                )

            # Now stream the response for real-time UI
            response_stream = client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=config,
            )

            # Stream chunks
            for chunk in response_stream:
                # Random delay for natural typing feel
                delay = self._get_typing_delay()
                await asyncio.sleep(delay)
                if chunk.text:
                    yield StreamEvent(
                        type=StreamEventType.TEXT_DELTA,
                        text_delta=TextDelta(content=chunk.text),
                        error=None,
                        finish_reason=None,
                        usage=None,
                    )

            # Yield completion event with token usage
            finish_reason = "STOP"
            if complete_response.candidates and len(complete_response.candidates) > 0:
                finish_reason = str(complete_response.candidates[0].finish_reason)

            yield StreamEvent(
                type=StreamEventType.MESSAGE_COMPLETE,
                text_delta=None,
                error=None,
                finish_reason=finish_reason,
                usage=usage,
            )

        except Exception as e:
            yield StreamEvent(
                type=StreamEventType.ERROR,
                text_delta=None,
                error=str(e),
                finish_reason=None,
                usage=None,
            )

    async def _non_stream_response(
        self, client, model, contents, config
    ) -> StreamEvent:
        """Handle non-streaming responses"""
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )

            text = response.text if response.text else None

            usage_info = self._extract_token_usage(response)
            usage = None

            if usage_info:
                usage = TokenUsage(
                    prompt_tokens=usage_info["prompt_tokens"],
                    completetion_tokens=usage_info["completion_tokens"],
                    cached_tokens=usage_info["cached_tokens"],
                    total_tokens=usage_info["total_tokens"],
                )

            finish_reason = None
            if response.candidates and len(response.candidates) > 0:
                finish_reason = str(response.candidates[0].finish_reason)

            return StreamEvent(
                type=StreamEventType.MESSAGE_COMPLETE,
                text_delta=TextDelta(content=text) if text else None,
                finish_reason=finish_reason,
                usage=usage,
                error=None,
            )

        except Exception as e:
            return StreamEvent(
                type=StreamEventType.ERROR,
                text_delta=None,
                error=str(e),
                finish_reason=None,
                usage=None,
            )

    def _extract_token_usage(self, response):
        """Extract token usage from Gemini response"""
        usage_info = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cached_tokens": 0,
        }

        if hasattr(response, "usage_metadata"):
            usage_info["prompt_tokens"] = response.usage_metadata.prompt_token_count
            usage_info["completion_tokens"] = (
                response.usage_metadata.candidates_token_count
            )
            usage_info["total_tokens"] = response.usage_metadata.total_token_count
            usage_info["cached_tokens"] = getattr(
                response.usage_metadata, "cached_content_token_count", 0
            )

        elif hasattr(response, "_result") and hasattr(
            response._result, "usage_metadata"
        ):
            usage = response._result.usage_metadata
            usage_info["prompt_tokens"] = usage.prompt_token_count
            usage_info["completion_tokens"] = usage.candidates_token_count
            usage_info["total_tokens"] = usage.total_token_count
            usage_info["cached_tokens"] = getattr(
                usage, "cached_content_token_count", 0
            )

        return usage_info
