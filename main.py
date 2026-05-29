import asyncio
from client.llm_client import LLMClient


async def main():
    client = LLMClient()
    messages = [{"role": "user", "content": "Whats up?"}]
    async for event in client.chat_completetion(messages, False):
        print(event)
    await client.close()
 

asyncio.run(main())
