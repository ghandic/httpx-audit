import inspect
import json
import contextlib
from typing import Any, Callable, Optional
from pydantic import BaseModel

import httpx


class Request(BaseModel):
    method: str
    url: str
    content: dict | str
    headers: dict[str, str]


class Response(BaseModel):
    status_code: int
    reason_phrase: str
    http_version: str
    url: str
    headers: dict[str, str]
    content: dict | str
    encoding: Optional[str]
    is_redirect: bool
    cookies: dict[str, str]
    elapsed: str


def request_to_pydantic(request: httpx.Request) -> Request:
    initial = {
        "method": request.method,
        "url": str(request.url),
        "content": request.content.decode("utf-8"),
        "headers": dict(request.headers),
    }
    with contextlib.suppress(json.JSONDecodeError):
        initial["content"] = json.loads(request.content.decode("utf-8"))
    return Request(**initial)


def response_to_pydantic(response: httpx.Response) -> Response:
    initial = {
        "status_code": response.status_code,
        "reason_phrase": response.reason_phrase,
        "http_version": response.http_version,
        "url": str(response.url),
        "headers": dict(response.headers),
        "content": response.text or "",
        "encoding": response.encoding,
        "is_redirect": response.is_redirect,
        "cookies": dict(response.cookies),
        "elapsed": str(response.elapsed),
    }
    with contextlib.suppress(json.JSONDecodeError):
        initial["content"] = response.json()
    return Response(**initial)


Hooks = list[Callable[..., Any]]


class CustomClient(httpx.AsyncClient):
    def __init__(
        self,
        request_hooks: Optional[Hooks] = None,
        response_hooks: Optional[Hooks] = None,
        event_hooks: Optional[dict[str, Hooks]] = None,
        **kwargs: Any,
    ) -> None:
        self.request_hooks = [] if request_hooks is None else request_hooks
        self.response_hooks = [] if response_hooks is None else response_hooks

        event_hooks = {} if event_hooks is None else event_hooks
        event_hooks = {
            "request": list(event_hooks.get("request", [])),
            "response": list(event_hooks.get("response", [])),
        }
        event_hooks["request"].append(self.__action_request)
        event_hooks["response"].append(self.__action_response)

        super().__init__(event_hooks=event_hooks, **kwargs)

    async def __action_request(self, request: httpx.Request) -> None:
        await request.aread()
        _request = request_to_pydantic(request)
        await self.__action_hooks(self.request_hooks, _request)

    async def __action_response(self, response: httpx.Response) -> None:
        await response.aread()
        _response = response_to_pydantic(response)
        await self.__action_hooks(self.response_hooks, _response)

    async def __action_hooks(self, hooks, obj):
        for hook in hooks:
            obj = await hook(obj) if inspect.iscoroutinefunction(hook) else hook(obj)
