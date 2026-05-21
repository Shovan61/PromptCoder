import os
from typing import Any, AsyncGenerator
from google import genai
from google.genai import types
from dotenv import load_dotenv

from client.response import EventType, StreamEvent, TokenUsage

# from client.response import TokenUsage

# Load variables from .env
load_dotenv()


class LLMClient:
    def __init__(self) -> None:
        self._client: genai.Client | None = None

    def get_client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(
                api_key=os.getenv("GEMINI_API_KEY"),
            )
        return self._client

    async def close(self) -> None:
        # Gemini client doesn't need explicit closing, but keeping for compatibility
        self._client = None

    async def chat_completetion(
        self, messages: list[dict[str, Any]], stream: bool = True
    ) -> AsyncGenerator[StreamEvent, None]:
        client = self.get_client()
        model = "gemini-3-flash-preview"

        # Convert your messages format to Gemini's format
        contents = self._convert_messages_to_gemini_format(messages)

        # Configure generation
        generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_level="HIGH",
            ),
        )

        if stream:
            await self._stream_response(
                client, model, contents, generate_content_config
            )
        else:
            event = await self._non_stream_response(
                client, model, contents, generate_content_config
            )
            yield event
        return

    def _convert_messages_to_gemini_format(self, messages: list[dict[str, Any]]):
        """Convert OpenAI-style messages to Gemini format"""
        contents = []
        for msg in messages:
            # Convert role names
            if msg["role"] == "assistant":
                role = "model"
            elif msg["role"] == "system":
                # Handle system messages by adding as user with prefix
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

    async def _stream_response(self, client, model, contents, config):
        """Handle streaming responses"""
        try:
            response_stream = client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=config,
            )

            for chunk in response_stream:
                if chunk.text:
                    print(chunk.text, end="", flush=True)
            print()

        except Exception as e:
            print(f"Streaming error: {e}")
            raise

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
            text = None
            if response.text:
                text_delta = text

            usage_info = self._extract_token_usage(response)
            usage = None

            if usage_info:
                usage = TokenUsage(
                    prompt_tokens=usage_info["prompt_tokens"],
                    completetion_tokens=usage_info["completion_tokens"],
                    cached_tokens=usage_info["cached_tokens"],
                    total_tokens=usage_info["total_tokens"],
                )
            print(response.candidates[0].finish_reason)
            return StreamEvent(
                type=EventType.MESSAGE_COMPLETE,
                text_delta=text_delta,
                finish_reason=str(response.candidates[0].finish_reason),
                usage=usage,
            )

        except Exception as e:
            print(f"API Error: {e}")
            raise

    def _extract_token_usage(self, response):
        """Extract token usage from Gemini response"""
        usage_info = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cached_tokens": 0,
        }

        # Try to get usage metadata from response
        if hasattr(response, "usage_metadata"):
            usage_info["prompt_tokens"] = response.usage_metadata.prompt_token_count
            usage_info["completion_tokens"] = (
                response.usage_metadata.candidates_token_count
            )
            usage_info["total_tokens"] = response.usage_metadata.total_token_count
            usage_info["cached_tokens"] = getattr(
                response.usage_metadata, "cached_content_token_count", 0
            )

        # Alternative way to get token counts
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
