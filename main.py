# main.py
import asyncio
from functools import wraps
import sys
from agent.agent import Agent
from agent.events import AgentEventType
import click
from ui.tui import TUI, get_console

console = get_console()


class CLI:
    def __init__(self):
        self.agent: Agent | None = None
        self.tui = TUI(console=console)

    async def run_single(self, message: str) -> str | None:
        async with Agent() as agent:
            self.agent = agent
            return await self._process_message(message)

    async def _process_message(self, message: str) -> str | None:
        if not self.agent:
            return None

        final_response = None
        assistant_streaming = False

        async for event in self.agent.run(message):
            if event.type == AgentEventType.TEXT_DELTA:
                content = event.data.get("content", "")
                if not assistant_streaming:
                    self.tui.begin_assistant()
                    assistant_streaming = True

                self.tui.stream_assistant_delta(content=content)
            elif event.type == AgentEventType.TEXT_COMPLETE:
                assistant_streaming = False
            elif event.type == AgentEventType.AGENT_ERROR:
                error = event.data.get("ERROR", "Unknown error")
                console.print(f"[error]Error: {error}[/error]")
                return None

        # Print a newline after the response
        console.print()

        # Return the final response or a default message
        return final_response if final_response else "No response received"


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
        result = await cli.run_single(prompt)
        if result is None:
            console.print("[error]No response received![/error]")
            sys.exit(1)
        else:
            # Optional: Show that we got a result
            console.print(f"[dim]✓ Response received ({len(result)} characters)[/dim]")
    else:
        click.echo("Please provide a prompt. Usage: python main.py 'Your prompt here'")
        return


if __name__ == "__main__":
    main()
