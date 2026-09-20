import os

import  httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import BaseModel

KEYCLOAK_BASE_URI = os.environ.get("KEYCLOAK_BASE_URI", "http://127.0.0.1:8080")
N8N_WEBHOOK_URL = os.environ.get(
    "N8N_WEBHOOK_URL",
    "http://localhost:5678/webhook/27c75e4f-890f-4e5e-aa96-2e22f04e9ee8",
)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{KEYCLOAK_BASE_URI}/realms/ai-agentic/protocol/openid-connect/auth",
    tokenUrl=f"{KEYCLOAK_BASE_URI}/realms/ai-agentic/protocol/openid-connect/token",
)
router = APIRouter(
    tags=["Recruitment"],
    prefix="/api/v1/recruitment",

)

class HiringRequest(BaseModel):
    position: str
    job_description: str

@router.post("/screen")
async def screen_candidates(request:HiringRequest, token: str = Depends(oauth2_scheme)):

    try:
        payload = {
            "position": request.position,
            "job_description": request.job_description,
        }
        headers = {
            "Authorization": f"Bearer {token}"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                N8N_WEBHOOK_URL,
                json=payload,
                headers=headers,
            )
        response.raise_for_status()

        return {
            "message": "Hiring workflow started successfully",
            "position": request.position,
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"n8n returned HTTP {e.response.status_code}",
        ) from e

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to n8n",
        ) from e