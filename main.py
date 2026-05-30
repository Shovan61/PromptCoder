import asyncio
from functools import wraps
from client.llm_client import LLMClient


import click


class CLI:
    def __init__(self):
        pass

    def run_single():
        pass


def async_command(f):
    """Decorator to make Click work with async functions"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.command()
@click.argument("prompt", required=False)
@async_command
async def main(prompt: str | None):
    if prompt is None:
        # If no prompt provided, show help
        click.echo("Please provide a prompt. Usage: python main.py 'Your prompt here'")
        return

    print(prompt)
    

main()
