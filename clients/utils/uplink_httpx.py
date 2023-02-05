import asyncio
import contextlib
import logging
from functools import wraps

from uplink.clients import exceptions, interfaces, io
import httpx

log = logging.getLogger("uplink.httpx")
ssl_context = httpx.create_ssl_context()


def threaded_callback(callback):
    @wraps(callback)
    async def new_callback(*args, **kwargs):
        return callback(*args, **kwargs)

    return new_callback


class HttpxClient(interfaces.HttpClientAdapter):
    exceptions = exceptions.Exceptions()

    def __init__(self, session=None, verify=True, **kwargs):
        self._session = session or httpx.AsyncClient(verify=ssl_context if verify else False, **kwargs)
        self._sync_callback_adapter = threaded_callback

    def __del__(self):
        log.debug("HttpxClient: __del__")
        with contextlib.suppress(RuntimeError):
            if not self._session.is_closed:
                asyncio.run(self._session.aclose())

    async def __aenter__(self):
        log.debug("HttpxClient: __aenter__")
        await self._session.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        log.debug("HttpxClient: __aexit__")
        await self._session.__aexit__()

    async def send(self, request):
        method, url, extras = request
        return await self._session.request(method=method, url=url, **extras)

    def wrap_callback(self, callback):
        if not asyncio.iscoroutinefunction(callback):
            callback = self._sync_callback_adapter(callback)
        return callback

    def apply_callback(self, callback, response):
        return self.wrap_callback(callback)(response)

    @staticmethod
    def io():
        return io.AsyncioStrategy()


HttpxClient.exceptions.BaseClientException = httpx.HTTPStatusError
HttpxClient.exceptions.ConnectionError = httpx.RequestError
HttpxClient.exceptions.ConnectionTimeout = httpx.TimeoutException
HttpxClient.exceptions.ServerTimeout = httpx.TimeoutException
HttpxClient.exceptions.SSLError = httpx.RequestError
HttpxClient.exceptions.InvalidURL = httpx.InvalidURL
