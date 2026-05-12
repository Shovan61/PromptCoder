import os
from typing import Any
from google import genai
from google.genai import types
from dotenv import load_dotenv

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

    async def chat_completetion(  # Keeping your original method name with typo
        self, messages: list[dict[str, Any]], stream: bool = True
    ):
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
            await self._stream_response(client, model, contents, generate_content_config)
        else:
            await self._non_stream_response(client, model, contents, generate_content_config)

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
            print()  # New line after stream ends
            
        except Exception as e:
            print(f"Streaming error: {e}")
            raise

    async def _non_stream_response(self, client, model, contents, config):
        """Handle non-streaming responses"""
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            print(response.text)
            
        except Exception as e:
            print(f"API Error: {e}")
            raise