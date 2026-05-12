import asyncio
from client.llm_client import LLMClient


async def main():
    client = LLMClient()
    messages = [{"role": "user", "content": "Whats up?"}]  
    await client.chat_completetion(messages, False) 
    await client.close()  # Added proper cleanup
    print("done")


asyncio.run(main())