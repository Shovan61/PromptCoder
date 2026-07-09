from dataclasses import dataclass
from typing import Any

from client.llm_client import LLMClient
from prompts.system import get_system_prompt


@dataclass
class MessageItem:
    role: str
    content: str
    token_count: int | None


class ContextManager:
    def __init__(self) -> None:
        self._client = LLMClient()

        self._system_prompt = get_system_prompt()
        self._messages: list[MessageItem] = []

    def add_user_message(self, content: str) -> None:
        item = MessageItem(
            role="user", content=content, token_count=self._client(content, False)
        )

        self._messages.append(item)

    def add_assistant_message(self, content: str) -> None:
        item = MessageItem(
            role="assistant",
            content=content or "",
            token_count=self._client(content, False),
        )

        self._messages.append(item)

    def get_messages(self) -> list[dict[str, Any]]:
        messages = []

        if self._system_prompt:
            messages.append({"role": "system", "content": self._system_prompt})
