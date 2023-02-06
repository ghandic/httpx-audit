from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from aiopath import AsyncPath
from jsonpath_ng import parse
from opentelemetry import trace
from pydantic import BaseModel

tracer = trace.get_tracer(__name__)


@asynccontextmanager
async def start_as_current_span_async(tracer, *args, **kwargs):
    with tracer.start_as_current_span(*args, **kwargs) as span:
        yield span


class TimeSaver:
    def __init__(self, name: str) -> None:
        self.name = AsyncPath(name)
        Path(name).mkdir(parents=True, exist_ok=True)

    @start_as_current_span_async(tracer, "save")
    async def save(self, model: BaseModel) -> BaseModel:
        file = self.name / f"{datetime.now().isoformat()}.json"
        await file.write_text(model.json())
        return model


@start_as_current_span_async(tracer, "try_assign_json_path")
async def try_assign_json_path(data: dict, path: str, assign: Any, sep: str = ".") -> dict:
    if not isinstance(data, dict):
        return data

    matches = parse(path).find(data)
    for match in matches:
        match.context.value[path.split(".")[-1]] = assign
    return data
