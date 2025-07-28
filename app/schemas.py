from pydantic import BaseModel

class ProfileCreate(BaseModel):
    child_age: int
    city: str
    strengths: str | None = None
    needs: str | None = None
    notes: str | None = None

class Profile(ProfileCreate):
    id: int

    class Config:
        from_attributes = True