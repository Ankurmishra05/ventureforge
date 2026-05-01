from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.predictions import router as predictions_router
from app.api.routes.startup import router as startup_router
from app.api.routes.export import router as export_router

from app.core.config import settings
from app.models.generation import Generation
from app.models.startup_project import StartupProject
from app.models.user import User

app = FastAPI(title=settings.app_name, version=settings.app_version)

User.__table__
StartupProject.__table__
Generation.__table__

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(startup_router)
app.include_router(export_router)
app.include_router(predictions_router)
