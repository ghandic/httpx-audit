import asyncio

from opentelemetry import trace

from clients.json_placeholder import JSONPlaceholder, Todo
from clients.utils.uplink_httpx import HttpxClient
from custom_client import CustomClient, Request, Response
from utils import TimeSaver, start_as_current_span_async, try_assign_json_path

tracer = trace.get_tracer(__name__)


@start_as_current_span_async(tracer, "obfuscate_url")
async def obfuscate_url(request: Request) -> Request:
    request.url = request.url.replace("jsonplaceholder", "*****")
    return request


@start_as_current_span_async(tracer, "obfuscate_response")
async def obfuscate_response(response: Response) -> Response:
    response.content = await try_assign_json_path(response.content, "title", "*****")
    return response


@start_as_current_span_async(tracer, "log")
async def log(obj: Request | Response) -> Request | Response:
    print(obj)
    return obj


@start_as_current_span_async(tracer, "demo_basic")
async def demo_basic(client: CustomClient, id: int) -> Todo:
    response = await client.get(f"https://jsonplaceholder.typicode.com/todos/{id}")
    # Apply validations using pydantic
    todo = Todo(**response.json())
    print(todo)
    return todo


@start_as_current_span_async(tracer, "demo_uplink")
async def demo_uplink(client: CustomClient, id: int) -> Todo:
    json_placeholder = JSONPlaceholder(
        base_url="https://jsonplaceholder.typicode.com",
        client=HttpxClient(session=client),
    )
    todo = await json_placeholder.get_todo(id)  # Auto applies validations using pydantic
    print(todo)
    return todo


async def get_client():
    saver = TimeSaver("log")
    obfuscated_saver = TimeSaver("obfuscated_log")

    request_hooks = [
        saver.save,  # Save the full object for audit
        obfuscate_url,  # Apply obfuscations
        obfuscated_saver.save,  # Save the full obfuscated object for debugging
        # Note, with saving in practice you will want to correlate a request/response pair, and possibly even use tenacity to add complex retry logic
        log,  # Log out to stout (print)
    ]
    response_hooks = [
        saver.save,  # Save the full object for audit
        obfuscate_response,  # Apply obfuscations
        obfuscated_saver.save,  # Save the full obfuscated object for debugging
        # Note, with saving in practice you will want to correlate a request/response pair, and possibly even use tenacity to add complex retry logic
        log,  # Log out to stout (print)
    ]
    return CustomClient(
        request_hooks=request_hooks,
        response_hooks=response_hooks,
    )


async def main() -> None:
    client = await get_client()
    await asyncio.gather(*[demo_basic(client, i + 1) for i in range(10)])
    await asyncio.gather(*[demo_uplink(client, i + 1) for i in range(10)])


if __name__ == "__main__":
    asyncio.run(main())
