import os
import tempfile
import torch
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2AuthorizationCodeBearer
from pathlib import Path

from utils.modelTrainer import ModelTrainer

router = APIRouter(
    tags=["vision"],
    prefix="/api/v1/vision",
)

KEYCLOAK_BASE_URI = os.environ.get("KEYCLOAK_BASE_URI", "http://127.0.0.1:8080")

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{KEYCLOAK_BASE_URI}/realms/ai-agentic/protocol/openid-connect/auth",
    tokenUrl=f"{KEYCLOAK_BASE_URI}/realms/ai-agentic/protocol/openid-connect/token",
)

model, transform, classes = ModelTrainer.load_model("models", "vit.pth")
device: str = "cuda" if torch.cuda.is_available() else "cpu"


@router.post("/predict")
async def predict(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type")
    suffix = Path(file.filename or "").suffix

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        image_path = tmp.name
    try:
        pred_class, pred_probs = ModelTrainer.prediction(
            model=model,
            image_path=image_path,
            device=device,
            classes=classes,
            transform=transform,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        os.unlink(image_path)
    return {"pred": pred_class, "probs": pred_probs}
