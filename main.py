from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional

app = FastAPI(title="Person API", version="1.0.0")

# Person model
class Person(BaseModel):
    id: int
    name: str
    age: int
    email: str

class PersonCreate(BaseModel):
    name: str
    age: int
    email: str

class PersonUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None

# In-memory storage
persons_db: Dict[int, Person] = {}
next_id = 1

@app.get("/")
def root():
    return {"message": "Person API - Use /docs for API documentation"}

@app.get("/persons", response_model=Dict[int, Person])
def get_all_persons():
    """Get all persons"""
    return persons_db

@app.get("/persons/{person_id}", response_model=Person)
def get_person(person_id: int):
    """Get a specific person by ID"""
    if person_id not in persons_db:
        raise HTTPException(status_code=404, detail="Person not found")
    return persons_db[person_id]

@app.post("/persons", response_model=Person, status_code=201)
def create_person(person_data: PersonCreate):
    """Create a new person"""
    global next_id
    
    person = Person(
        id=next_id,
        name=person_data.name,
        age=person_data.age,
        email=person_data.email
    )
    persons_db[next_id] = person
    next_id += 1
    
    return person

@app.put("/persons/{person_id}", response_model=Person)
def update_person(person_id: int, person_data: PersonUpdate):
    """Update an existing person"""
    if person_id not in persons_db:
        raise HTTPException(status_code=404, detail="Person not found")
    
    person = persons_db[person_id]
    
    # Update only provided fields
    if person_data.name is not None:
        person.name = person_data.name
    if person_data.age is not None:
        person.age = person_data.age
    if person_data.email is not None:
        person.email = person_data.email
    
    persons_db[person_id] = person
    return person

@app.delete("/persons/{person_id}", status_code=204)
def delete_person(person_id: int):
    """Delete a person"""
    if person_id not in persons_db:
        raise HTTPException(status_code=404, detail="Person not found")
    
    del persons_db[person_id]
    return None
