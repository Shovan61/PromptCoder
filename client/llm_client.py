import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

class LLMClient:
    def __init__(self) -> None:
        self._client: AsyncOpenAI | None = None

    def get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL")
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None
