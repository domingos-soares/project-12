from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import engine, get_db, Base
from models import PersonModel

app = FastAPI(title="Person API", version="1.0.0")

# Create database tables
Base.metadata.create_all(bind=engine)

# Person model
class Person(BaseModel):
    id: int
    name: str
    age: int
    email: str
    
    class Config:
        from_attributes = True

class PersonCreate(BaseModel):
    name: str
    age: int
    email: str

class PersonUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None

# Pydantic schemas remain for API validation

@app.get("/")
def root():
    return {"message": "Person API - Use /docs for API documentation"}

@app.get("/health")
def healthcheck(db: Session = Depends(get_db)):
    """Check API and database health"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "api": "operational",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "api": "operational",
                "database": "disconnected",
                "error": str(e)
            }
        )

@app.get("/persons", response_model=List[Person])
def get_all_persons(db: Session = Depends(get_db)):
    """Get all persons"""
    persons = db.query(PersonModel).all()
    return persons

@app.get("/persons/{person_id}", response_model=Person)
def get_person(person_id: int, db: Session = Depends(get_db)):
    """Get a specific person by ID"""
    person = db.query(PersonModel).filter(PersonModel.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

@app.post("/persons", response_model=Person, status_code=201)
def create_person(person_data: PersonCreate, db: Session = Depends(get_db)):
    """Create a new person"""
    # Check if email already exists
    existing_person = db.query(PersonModel).filter(PersonModel.email == person_data.email).first()
    if existing_person:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_person = PersonModel(
        name=person_data.name,
        age=person_data.age,
        email=person_data.email
    )
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    
    return db_person

@app.put("/persons/{person_id}", response_model=Person)
def update_person(person_id: int, person_data: PersonUpdate, db: Session = Depends(get_db)):
    """Update an existing person"""
    person = db.query(PersonModel).filter(PersonModel.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Update only provided fields
    if person_data.name is not None:
        person.name = person_data.name
    if person_data.age is not None:
        person.age = person_data.age
    if person_data.email is not None:
        # Check if new email already exists for another user
        existing = db.query(PersonModel).filter(
            PersonModel.email == person_data.email,
            PersonModel.id != person_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        person.email = person_data.email
    
    db.commit()
    db.refresh(person)
    return person

@app.delete("/persons/{person_id}", status_code=204)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    """Delete a person"""
    person = db.query(PersonModel).filter(PersonModel.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    db.delete(person)
    db.commit()
    return None
