import asyncio
import logging

from fastapi import Depends, FastAPI

from logger import configure

app = FastAPI()
configure(app)

from main import CustomClient, demo_basic, demo_uplink, get_client

logger = logging.getLogger("demo")


@app.on_event("startup")
async def start_up():
    logger.info("Started service")


@app.get("/demo-uplink/{id}")
async def demo_single_uplink(id: int, client: CustomClient = Depends(get_client)):
    return await demo_uplink(client, id)


@app.get("/demo-basic/{id}")
async def demo_single_basic(id: int, client: CustomClient = Depends(get_client)):
    return await demo_basic(client, id)


@app.get("/demo-uplink")
async def demo_bulk_uplink(client: CustomClient = Depends(get_client)):
    return await asyncio.gather(*[demo_uplink(client, i + 1) for i in range(10)])


@app.get("/demo-basic")
async def demo_bulk_basic(client: CustomClient = Depends(get_client)):
    return await asyncio.gather(*[demo_basic(client, i + 1) for i in range(10)])
