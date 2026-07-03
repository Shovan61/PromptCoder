import asyncio
from functools import wraps
from agent.agent import Agent
from agent.events import AgentEventType
from client.llm_client import LLMClient


import click

from ui.tui import TUI, get_console

console = get_console()


class CLI:
    def __init__(self):

        self.agent: Agent | None = None
        self.tui = TUI(console=console)

    async def run_single(self, message: str):
        async with Agent() as agent:
            self.agent = agent
            self._process_message(message)

    async def _process_message(self, message: str) -> str | None:
        if not self.agent:
            return None
        async for event in self.agent.run(message):
            if event.type == AgentEventType.TEXT_DELTA:
                content = event.data.get("content", "")
                self.tui.stream_assistant_delta(content=content)


def async_command(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.command()
@click.argument("prompt", required=False)
@async_command
async def main(prompt: str | None):
    cli = CLI()
    if prompt:
        asyncio.run(cli.run_single(prompt))
    if prompt is None:
        # If no prompt provided, show help
        click.echo("Please provide a prompt. Usage: python main.py 'Your prompt here'")
        return


main()
