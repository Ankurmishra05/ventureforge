from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.generation import Generation
from app.models.startup_project import StartupProject
from app.models.user import User


def get_or_create_startup_project(
    db: Session, *, user: User, idea: str, audience: str
) -> StartupProject:
    project = (
        db.query(StartupProject)
        .filter(
            StartupProject.user_id == user.id,
            StartupProject.idea == idea,
            StartupProject.audience == audience,
        )
        .first()
    )

    if project is not None:
        return project

    project = StartupProject(user_id=user.id, idea=idea, audience=audience)
    db.add(project)
    db.flush()
    return project


def save_generation(
    db: Session,
    *,
    user: User,
    idea: str,
    audience: str,
    outputs: dict,
    provider_used: str,
) -> Generation:
    project = get_or_create_startup_project(db, user=user, idea=idea, audience=audience)
    generation = Generation(
        user_id=user.id,
        startup_project_id=project.id,
        idea=idea,
        audience=audience,
        outputs=outputs,
        provider_used=provider_used,
    )
    project.updated_at = datetime.now(timezone.utc)
    db.add(generation)
    db.commit()
    db.refresh(generation)
    return generation
