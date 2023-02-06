from pydantic import BaseModel
from uplink import Consumer, Path, get


class Todo(BaseModel):
    userId: int
    id: int
    title: str
    completed: bool


class JSONPlaceholder(Consumer):
    """A Python Client for the JSONPlaceholder API."""

    @get("todos/{todo}")
    async def get_todo(self, todo: Path) -> Todo:
        """Get a todo."""
