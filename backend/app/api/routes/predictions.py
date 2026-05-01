from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.startup import (
    FutureFundingPredictionRequest,
    FutureFundingPredictionResponse,
)
from app.services.outcome_model import predict_future_funding

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("/future-funding", response_model=FutureFundingPredictionResponse)
def predict_future_funding_endpoint(
    req: FutureFundingPredictionRequest,
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    return predict_future_funding(req.model_dump())
