import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer

from graph.graph import app

KEYCLOAK_BASE_URI = os.environ.get("KEYCLOAK_BASE_URI", "http://127.0.0.1:8080")

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{KEYCLOAK_BASE_URI}/realms/ai-agentic/protocol/openid-connect/auth",
    tokenUrl=f"{KEYCLOAK_BASE_URI}/realms/ai-agentic/protocol/openid-connect/token",
)
router = APIRouter(
    tags=["resume"],
    prefix="/api/v1/resume",
)


@router.post("/analyze")
async def analyze_resume(job_role: str, file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported",
                            )
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp.flush()

        response = await app.ainvoke({"file_path": tmp.name, "job_role": job_role})

        return {"summary": response["generation"].content}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
