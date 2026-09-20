import os
from contextlib import asynccontextmanager

import py_eureka_client.eureka_client as eureka_client
from fastapi import FastAPI

from app.router.resume import router

EUREKA_SERVER_URL = os.environ.get("EUREKA_SERVER_URL", "http://localhost:8761/eureka/")
INSTANCE_HOST = os.environ.get("INSTANCE_HOST", "127.0.0.1")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register with Eureka
    await eureka_client.init_async(
        eureka_server=EUREKA_SERVER_URL,
        app_name="RESUME-INTELLIGENCE",
        instance_id=f"{INSTANCE_HOST}:resume-intelligence:8002",
        instance_host=INSTANCE_HOST,
        instance_port=8002,
    )

    print("Resume Intelligence registered with Eureka")

    yield

    # Stop Eureka client
    await eureka_client.stop_async()

    print("Resume Intelligence unregistered from Eureka")


app = FastAPI(
    title="Resume Intelligence Service",
    version="0.1.0",
    openapi_url="/api/v1/resume/openapi.json",
    docs_url="/docs",
    lifespan=lifespan,
)

app.include_router(router)
