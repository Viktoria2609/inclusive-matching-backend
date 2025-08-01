from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import profiles
from app.database import Base, engine
from app import models

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles.router, prefix="/profiles", tags=["Profiles"])

@app.get("/")
def root():
    return {"message": "Inclusive Matching API is running!"}