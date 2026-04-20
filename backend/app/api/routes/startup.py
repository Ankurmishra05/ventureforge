from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.generation import Generation
from app.models.user import User
from app.schemas.history import GenerationHistoryItem, GenerationHistoryResponse
from app.schemas.startup import StartupRequest, StartupResponse
from app.services.persistence import save_generation
from app.workflows.orchestrator import generate_startup_plan

router = APIRouter(tags=["startup"])


@router.get("/")
def root():
    return {"message": "VentureForge API Running"}


@router.post("/generate-startup", response_model=StartupResponse)
def generate(
    req: StartupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = generate_startup_plan(req.idea, req.audience)
    startup_response = {
    "idea": result["idea"],
    "user_email": current_user.email,
    "research": result["research"],
    "branding": result["branding"],
    "finance": result["finance"],
    "decision": result["decision"],   # 🔥 THIS LINE WAS MISSING
}
    save_generation(
        db,
        user=current_user,
        idea=req.idea,
        audience=req.audience,
        outputs=startup_response,
        provider_used=result["provider_used"],
    )
    return startup_response


@router.get("/startup-history", response_model=GenerationHistoryResponse)
def get_startup_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Generation)
        .filter(Generation.user_id == current_user.id)
        .order_by(Generation.created_at.desc())
        .limit(limit)
        .all()
    )

    return GenerationHistoryResponse(
        items=[
            GenerationHistoryItem(
                generation_id=row.id,
                startup_project_id=row.startup_project_id,
                idea=row.idea,
                audience=row.audience,
                provider_used=row.provider_used,
                outputs=row.outputs,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]
    )
