from __future__ import annotations

import abc
from enum import Enum

from pathlib import Path
from pydantic import BaseModel, ValidationError
from enum import Enum
from typing import Any
from dataclasses import dataclass, field

from pydantic.json_schema import model_json_schema


class ToolKind(str, Enum):
    READ = "read"
    WRITE = "write"
    SHELL = "shell"
    NETWORK = "network"
    MEMORY = "memory"
    MCP = "mcp"


@dataclass
class ToolInvocation:
    params: dict[str, Any]
    cwd: Path


class ToolResult:
    success: bool
    output: str
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    truncated: bool = False
    # diff: FileDiff | None = None
    exit_code: int | None = None

    @classmethod
    def error_result(cls, error: str, output: str = "", **kwargs: Any):
        return cls(
            success=False,
            output=output,
            error=error,
            **kwargs,
        )

    @classmethod
    def success_result(cls, output: str, **kwargs: Any):
        return cls(
            success=True,
            output=output,
            error=None,
            **kwargs,
        )


class Tool(abc.ABC):
    name: str = "base_tool"
    description: str = "Base tool"
    kind: ToolKind = ToolKind.READ

    def __init__(self):
        super().__init__()

    @property
    def schema(self) -> dict[str, Any] | type["BaseModel"]:
        raise NotImplementedError("Tool must define schema property or class attribute")

    @abc.abstractmethod
    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        pass

    def validate_params(self, params: dict[str, Any]) -> list[str]:
        schema = self.schema
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            try:
                schema(**params)
            except ValidationError as e:
                errors = []
                for error in e.errors():
                    field = ".".join(str(x) for x in error.get("loc", []))
                    msg = error.get("msg", "Validation error")
                    errors.append(f"Parameter '{field}': {msg}")

                return errors
            except Exception as e:
                return [str(e)]

        return []

    def is_mutating(self, params: dict[str, Any]) -> None:
        return self.kind in {
            ToolKind.WRITE,
            ToolKind.SHELL,
            ToolKind.NETWORK,
            ToolKind.MEMORY,
        }

    async def get_confirmation(
        self, invocation: ToolInvocation
    ) -> None | ToolInvocation:
        pass

    def to_gemini_schema(self) -> dict[str, Any]:
        # """
        # Convert tool schema to Gemini API format.

        # Gemini's function declaration format:
        # {
        #     "name": "function_name",
        #     "description": "Function description",
        #     "parameters": {
        #         "type": "object",
        #         "properties": {
        #             "param1": {
        #                 "type": "string",
        #                 "description": "Parameter description"
        #             }
        #         },
        #         "required": ["param1"]
        #     }
        # }
        # """
        schema = self.schema

        if isinstance(schema, type) and issubclass(schema, BaseModel):
            # Convert Pydantic model to JSON schema
            json_schema = model_json_schema(schema, mode="serialization")

            # Gemini uses this format ->
            return {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": json_schema.get("properties", {}),
                    "required": json_schema.get("required", []),
                },
            }

        if isinstance(schema, dict):
            # If schema is already a dict, ensure it's in the right format
            result = {
                "name": self.name,
                "description": self.description,
            }

            if "parameters" in schema:
                result["parameters"] = schema["parameters"]
            else:
                result["parameters"] = schema

            return result

        raise ValueError(f"Invalid schema type for tool {self.name}: {type(schema)}")
