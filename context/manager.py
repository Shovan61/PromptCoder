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
        self._total_tokens: int | None = None

    def _count_tokens_for_message(self, content: str) -> int:
        """Count tokens for a single message using Gemini's token counter"""
        if not content:
            return 0
        
        # Gemini expects messages in a specific format
        messages = [{"role": "user", "content": content}]
        return self._client.count_tokens(messages)

    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation context"""
        item = MessageItem(
            role="user", 
            content=content, 
            token_count=self._count_tokens_for_message(content)
        )
        self._messages.append(item)
        self._total_tokens = None  # Invalidate cache

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the conversation context"""
        # Handle None or empty content
        content_str = content or ""
        item = MessageItem(
            role="assistant",
            content=content_str,
            token_count=self._count_tokens_for_message(content_str) if content_str else 0
        )
        self._messages.append(item)
        self._total_tokens = None  # Invalidate cache

    def add_system_message(self, content: str) -> None:
        """Add a system message to the conversation context"""
        item = MessageItem(
            role="system",
            content=content,
            token_count=self._count_tokens_for_message(content)
        )
        self._messages.append(item)
        self._total_tokens = None  # Invalidate cache

    def get_messages(self) -> list[dict[str, Any]]:
        """Get all messages in OpenAI-compatible format for the LLM client"""
        messages = []

        # Add system prompt first if it exists
        if self._system_prompt:
            messages.append({"role": "system", "content": self._system_prompt})

        # Add conversation history
        for item in self._messages:
            messages.append(item.to_dict())

        return messages

    def get_total_token_count(self) -> int:
        """Get total token count for all messages (cached for performance)"""
        if self._total_tokens is None:
            messages = self.get_messages()
            if messages:
                self._total_tokens = self._client.count_tokens(messages)
            else:
                self._total_tokens = 0
        return self._total_tokens

    def get_message_count(self) -> int:
        """Get the number of messages in the conversation"""
        return len(self._messages)

    def clear(self) -> None:
        """Clear conversation history (keeps system prompt)"""
        self._messages.clear()
        self._total_tokens = None

    def reset(self) -> None:
        """Reset everything including system prompt"""
        self._messages.clear()
        self._system_prompt = get_system_prompt()
        self._total_tokens = None

    def get_conversation_summary(self) -> dict[str, Any]:
        """Get a summary of the current conversation context"""
        return {
            "message_count": self.get_message_count(),
            "total_tokens": self.get_total_token_count(),
            "has_system_prompt": bool(self._system_prompt),
            "messages": [
                {"role": msg.role, "content_preview": msg.content[:50] + "..." if len(msg.content) > 50 else msg.content}
                for msg in self._messages
            ]
        }