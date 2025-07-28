from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter()
print("Schemas:", dir(schemas))

# 🔹 Create a new profile
@router.post("/", response_model=schemas.Profile, status_code=status.HTTP_201_CREATED)
def create_profile(profile: schemas.ProfileCreate, db: Session = Depends(get_db)):
    db_profile = models.Profile(**profile.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

# 🔹 Get all profiles
@router.get("/", response_model=list[schemas.Profile])
def get_profiles(db: Session = Depends(get_db)):
    return db.query(models.Profile).all()

# 🔹 Get a profile by ID
@router.get("/{profile_id}", response_model=schemas.Profile)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

# 🔹 Delete a profile by ID
@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(profile)
    db.commit()
    return