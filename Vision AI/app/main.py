import os

import py_eureka_client.eureka_client as eureka_client
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.router.predict import router

EUREKA_SERVER_URL = os.environ.get("EUREKA_SERVER_URL", "http://localhost:8761/eureka/")
INSTANCE_HOST = os.environ.get("INSTANCE_HOST", "127.0.0.1")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register with Eureka
    await eureka_client.init_async(
        eureka_server=EUREKA_SERVER_URL,
        app_name="VISION-AI",
        instance_id=f"{INSTANCE_HOST}:vision-ai:8001",
        instance_host=INSTANCE_HOST,
        instance_port=8001,
    )

    print("VISION-AI registered with Eureka")

    yield

    # Stop Eureka client
    await eureka_client.stop_async()

    print("VISION-AI unregistered from Eureka")


app = FastAPI(
    title="Vision AI",
    version="0.1.0",
    openapi_url="/api/v1/vision/openapi.json",
    docs_url="/docs",
    lifespan=lifespan,
)


app.include_router(router)
