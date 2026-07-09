from dataclasses import dataclass
from typing import Any

from client.llm_client import LLMClient
from prompts.system import get_system_prompt


@dataclass
class MessageItem:
    role: str
    content: str
    token_count: int | None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"role": self.role}

        if self.content:
            result["content"] = self.content

        return result


class ContextManager:
    def __init__(self) -> None:
        self._client = LLMClient()
        self._system_prompt = get_system_prompt()
        self._messages: list[MessageItem] = []

    def _count_tokens_for_text(self, content: str) -> int:
        """Count tokens for a single message using Gemini's token counter"""
        if not content:
            return 0

        # Gemini expects messages in a specific format
        messages = [{"role": "user", "content": content}]
        return self._client.count_tokens(messages)

    def add_user_message(self, content: str) -> None:
        item = MessageItem(
            role="user",
            content=content,
            token_count=self._count_tokens_for_text(content),
        )
        self._messages.append(item)

    def add_assistant_message(self, content: str) -> None:
        # Handle None or empty content
        content_str = content or ""
        item = MessageItem(
            role="assistant",
            content=content_str,
            token_count=self._count_tokens_for_text(content_str) if content_str else 0,
        )
        self._messages.append(item)

    def add_system_message(self, content: str) -> None:
        """Optional: Add system messages to context"""
        item = MessageItem(
            role="system",
            content=content,
            token_count=self._count_tokens_for_text(content),
        )
        self._messages.append(item)

    def get_messages(self) -> list[dict[str, Any]]:
        messages = []

        if self._system_prompt:
            messages.append({"role": "system", "content": self._system_prompt})

        for item in self._messages:
            messages.append(item.to_dict())

        return messages

    def get_token_count(self) -> int:
        """Get total token count for all messages"""
        total = 0
        if self._system_prompt:
            total += self._count_tokens_for_text(self._system_prompt)

        for msg in self._messages:
            if msg.token_count:
                total += msg.token_count

        return total

    def clear(self) -> None:
        """Clear conversation history (keeps system prompt)"""
        self._messages = []
