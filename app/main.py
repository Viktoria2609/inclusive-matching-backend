from fastapi import FastAPI
from app.routers import profiles
from app.database import Base, engine
from app import models

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(profiles.router, prefix="/profiles", tags=["Profiles"])

@app.get("/")
def root():
    return {"message": "Inclusive Matching API is running!"}