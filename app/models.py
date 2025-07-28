from sqlalchemy import Column, Integer, String
from app.database import Base  

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    child_age = Column(Integer, nullable=False)
    city = Column(String, nullable=False)
    strengths = Column(String)
    needs = Column(String)
    notes = Column(String)