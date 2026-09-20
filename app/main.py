from fastapi import FastAPI
from app.routers.auth import router as auth_router
from sqlalchemy import text
from app.routers.progress import router as progress_router
from app.database import engine, Base
from app import models
from app.routers.achievements import router as achievements_router
from app.routers import daily_challenge
from app.models import UserFavoriteWord
from app.routers import favorites
app = FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(auth_router)
app.include_router(progress_router)
app.include_router(achievements_router)
app.include_router(daily_challenge.router)
app.include_router(favorites.router)
@app.get("/")
def root():
    return {
        "message": "HolaLingo backend is running"
    }


