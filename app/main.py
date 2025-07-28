from fastapi import FastAPI
from fastapi import FastAPI
from app.routers import profiles
from app.database import Base, engine
from app import models

# Создание таблиц при запуске
Base.metadata.create_all(bind=engine)

# Инициализация FastAPI
app = FastAPI()

# Роуты
app.include_router(profiles.router, prefix="/profiles", tags=["Profiles"])

@app.get("/")
def root():
    return {"message": "Inclusive Matching API is running!"}