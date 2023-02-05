from datetime import datetime
from typing import Any

from pydantic import BaseModel
from jsonpath_ng import parse
from aiopath import AsyncPath


class TimeSaver:
    def __init__(self, name: str) -> None:
        self.name = AsyncPath(name)
        self.name.mkdir(parents=True, exist_ok=True)

    async def save(self, model: BaseModel) -> BaseModel:
        file = self.name / f"{datetime.now().isoformat()}.json"
        await file.write_text(model.json())
        return model


async def try_assign_json_path(data: dict, path: str, assign: Any, sep: str = ".") -> dict:
    if not isinstance(data, dict):
        return data

    matches = parse(path).find(data)
    for match in matches:
        match.context.value[path.split(".")[-1]] = assign
    return data
