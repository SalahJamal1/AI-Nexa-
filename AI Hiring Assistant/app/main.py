import os
from contextlib import asynccontextmanager

import py_eureka_client.eureka_client as eureka_client
from fastapi import FastAPI

from app.router.n8n_recruitment import router

EUREKA_SERVER_URL = os.environ.get("EUREKA_SERVER_URL", "http://localhost:8761/eureka/")
INSTANCE_HOST = os.environ.get("INSTANCE_HOST", "127.0.0.1")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register with Eureka
    await eureka_client.init_async(
        eureka_server=EUREKA_SERVER_URL,
        app_name="AI Hiring Assistant",
        instance_id=f"{INSTANCE_HOST}:ai-hiring-assistant:8003",
        instance_host=INSTANCE_HOST,
        instance_port=8003,
    )

    print("AI Hiring Assistant registered with Eureka")

    yield

    # Stop Eureka client
    await eureka_client.stop_async()

    print("Resume Intelligence unregistered from Eureka")


app = FastAPI(
    title="AI Hiring Assistant Service",
    version="0.1.0",
    openapi_url="/api/v1/recruitment/openapi.json",
    docs_url="/docs",
    lifespan=lifespan,
)

app.include_router(router)