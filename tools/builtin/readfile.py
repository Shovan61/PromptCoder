from pydantic import BaseModel, Field


class ReadFileParam(BaseModel):
    path: str = Field(
        ...,
        description="Path to the file to read (relative to working directory or absolute path)",
    )
    offset: int = Field(
        1,
        ge=1,
        description="Line number to start reading from (1-based6. Defualts to 1)",
    )

    limit: int | None = Field(
        None,
        ge=1,
        description="Maximum number of lines to read. If not specified, reads entire file",
    )
