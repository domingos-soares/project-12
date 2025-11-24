import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db
from models import PersonModel

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override the database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with database override"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root(self, client):
        """Test root endpoint returns welcome message"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Person API - Use /docs for API documentation"}


class TestHealthcheckEndpoint:
    """Tests for the healthcheck endpoint"""
    
    def test_healthcheck_success(self, client):
        """Test healthcheck returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["api"] == "operational"
        assert data["database"] == "connected"


class TestCreatePerson:
    """Tests for POST /persons endpoint"""
    
    def test_create_person_success(self, client):
        """Test successful person creation"""
        person_data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com"
        }
        response = client.post("/persons", json=person_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["age"] == 30
        assert data["email"] == "john@example.com"
        assert "id" in data
        assert data["id"] == 1
    
    def test_create_multiple_persons(self, client):
        """Test creating multiple persons"""
        persons = [
            {"name": "Alice", "age": 25, "email": "alice@example.com"},
            {"name": "Bob", "age": 35, "email": "bob@example.com"},
            {"name": "Charlie", "age": 45, "email": "charlie@example.com"}
        ]
        
        for i, person_data in enumerate(persons, start=1):
            response = client.post("/persons", json=person_data)
            assert response.status_code == 201
            data = response.json()
            assert data["id"] == i
            assert data["name"] == person_data["name"]
    
    def test_create_person_duplicate_email(self, client):
        """Test creating person with duplicate email fails"""
        person_data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com"
        }
        
        # First creation should succeed
        response = client.post("/persons", json=person_data)
        assert response.status_code == 201
        
        # Second creation with same email should fail
        duplicate_data = {
            "name": "Jane Doe",
            "age": 28,
            "email": "john@example.com"
        }
        response = client.post("/persons", json=duplicate_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"
    
    def test_create_person_missing_fields(self, client):
        """Test creating person with missing required fields"""
        incomplete_data = {"name": "John Doe"}
        response = client.post("/persons", json=incomplete_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_person_invalid_age_type(self, client):
        """Test creating person with invalid age type"""
        invalid_data = {
            "name": "John Doe",
            "age": "thirty",  # Should be integer
            "email": "john@example.com"
        }
        response = client.post("/persons", json=invalid_data)
        assert response.status_code == 422
    
    def test_create_person_negative_age(self, client):
        """Test creating person with negative age (currently allowed, could add validation)"""
        person_data = {
            "name": "John Doe",
            "age": -5,
            "email": "john@example.com"
        }
        response = client.post("/persons", json=person_data)
        assert response.status_code == 201  # Currently passes, could add validation


class TestGetAllPersons:
    """Tests for GET /persons endpoint"""
    
    def test_get_all_persons_empty(self, client):
        """Test getting all persons when database is empty"""
        response = client.get("/persons")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_all_persons_with_data(self, client):
        """Test getting all persons with data"""
        # Create test persons
        persons = [
            {"name": "Alice", "age": 25, "email": "alice@example.com"},
            {"name": "Bob", "age": 35, "email": "bob@example.com"}
        ]
        
        for person_data in persons:
            client.post("/persons", json=person_data)
        
        # Get all persons
        response = client.get("/persons")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Alice"
        assert data[1]["name"] == "Bob"


class TestGetPerson:
    """Tests for GET /persons/{person_id} endpoint"""
    
    def test_get_person_success(self, client):
        """Test getting a specific person by ID"""
        # Create a person
        person_data = {"name": "John Doe", "age": 30, "email": "john@example.com"}
        create_response = client.post("/persons", json=person_data)
        person_id = create_response.json()["id"]
        
        # Get the person
        response = client.get(f"/persons/{person_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == person_id
        assert data["name"] == "John Doe"
        assert data["age"] == 30
        assert data["email"] == "john@example.com"
    
    def test_get_person_not_found(self, client):
        """Test getting non-existent person returns 404"""
        response = client.get("/persons/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Person not found"
    
    def test_get_person_invalid_id_type(self, client):
        """Test getting person with invalid ID type"""
        response = client.get("/persons/abc")
        assert response.status_code == 422  # Validation error


class TestUpdatePerson:
    """Tests for PUT /persons/{person_id} endpoint"""
    
    def test_update_person_all_fields(self, client):
        """Test updating all fields of a person"""
        # Create a person
        person_data = {"name": "John Doe", "age": 30, "email": "john@example.com"}
        create_response = client.post("/persons", json=person_data)
        person_id = create_response.json()["id"]
        
        # Update all fields
        update_data = {"name": "Jane Doe", "age": 28, "email": "jane@example.com"}
        response = client.put(f"/persons/{person_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jane Doe"
        assert data["age"] == 28
        assert data["email"] == "jane@example.com"
    
    def test_update_person_partial(self, client):
        """Test partial update (only some fields)"""
        # Create a person
        person_data = {"name": "John Doe", "age": 30, "email": "john@example.com"}
        create_response = client.post("/persons", json=person_data)
        person_id = create_response.json()["id"]
        
        # Update only age
        update_data = {"age": 31}
        response = client.put(f"/persons/{person_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "John Doe"  # Unchanged
        assert data["age"] == 31  # Changed
        assert data["email"] == "john@example.com"  # Unchanged
    
    def test_update_person_not_found(self, client):
        """Test updating non-existent person returns 404"""
        update_data = {"name": "Jane Doe"}
        response = client.put("/persons/999", json=update_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Person not found"
    
    def test_update_person_duplicate_email(self, client):
        """Test updating person with email that already exists"""
        # Create two persons
        client.post("/persons", json={"name": "Alice", "age": 25, "email": "alice@example.com"})
        create_response = client.post("/persons", json={"name": "Bob", "age": 35, "email": "bob@example.com"})
        bob_id = create_response.json()["id"]
        
        # Try to update Bob's email to Alice's email
        update_data = {"email": "alice@example.com"}
        response = client.put(f"/persons/{bob_id}", json=update_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"
    
    def test_update_person_same_email(self, client):
        """Test updating person with their own email (should succeed)"""
        # Create a person
        create_response = client.post("/persons", json={"name": "John", "age": 30, "email": "john@example.com"})
        person_id = create_response.json()["id"]
        
        # Update with same email and different name
        update_data = {"name": "Johnny", "email": "john@example.com"}
        response = client.put(f"/persons/{person_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Johnny"
        assert data["email"] == "john@example.com"
    
    def test_update_person_empty_update(self, client):
        """Test updating person with no fields (should succeed with no changes)"""
        # Create a person
        person_data = {"name": "John Doe", "age": 30, "email": "john@example.com"}
        create_response = client.post("/persons", json=person_data)
        person_id = create_response.json()["id"]
        
        # Update with empty data
        response = client.put(f"/persons/{person_id}", json={})
        assert response.status_code == 200
        data = response.json()
        # All fields should remain unchanged
        assert data["name"] == "John Doe"
        assert data["age"] == 30
        assert data["email"] == "john@example.com"


class TestDeletePerson:
    """Tests for DELETE /persons/{person_id} endpoint"""
    
    def test_delete_person_success(self, client):
        """Test successful person deletion"""
        # Create a person
        person_data = {"name": "John Doe", "age": 30, "email": "john@example.com"}
        create_response = client.post("/persons", json=person_data)
        person_id = create_response.json()["id"]
        
        # Delete the person
        response = client.delete(f"/persons/{person_id}")
        assert response.status_code == 204
        assert response.content == b""
        
        # Verify person is deleted
        get_response = client.get(f"/persons/{person_id}")
        assert get_response.status_code == 404
    
    def test_delete_person_not_found(self, client):
        """Test deleting non-existent person returns 404"""
        response = client.delete("/persons/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Person not found"
    
    def test_delete_person_multiple_times(self, client):
        """Test deleting the same person twice fails on second attempt"""
        # Create a person
        person_data = {"name": "John Doe", "age": 30, "email": "john@example.com"}
        create_response = client.post("/persons", json=person_data)
        person_id = create_response.json()["id"]
        
        # First deletion should succeed
        response = client.delete(f"/persons/{person_id}")
        assert response.status_code == 204
        
        # Second deletion should fail
        response = client.delete(f"/persons/{person_id}")
        assert response.status_code == 404


class TestIntegrationScenarios:
    """Integration tests covering complete workflows"""
    
    def test_complete_crud_workflow(self, client):
        """Test complete CRUD workflow"""
        # Create
        person_data = {"name": "John Doe", "age": 30, "email": "john@example.com"}
        create_response = client.post("/persons", json=person_data)
        assert create_response.status_code == 201
        person_id = create_response.json()["id"]
        
        # Read
        read_response = client.get(f"/persons/{person_id}")
        assert read_response.status_code == 200
        assert read_response.json()["name"] == "John Doe"
        
        # Update
        update_data = {"age": 31}
        update_response = client.put(f"/persons/{person_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["age"] == 31
        
        # Delete
        delete_response = client.delete(f"/persons/{person_id}")
        assert delete_response.status_code == 204
        
        # Verify deletion
        verify_response = client.get(f"/persons/{person_id}")
        assert verify_response.status_code == 404
    
    def test_create_and_list_multiple_persons(self, client):
        """Test creating and listing multiple persons"""
        persons = [
            {"name": "Alice", "age": 25, "email": "alice@example.com"},
            {"name": "Bob", "age": 35, "email": "bob@example.com"},
            {"name": "Charlie", "age": 45, "email": "charlie@example.com"}
        ]
        
        # Create all persons
        for person_data in persons:
            response = client.post("/persons", json=person_data)
            assert response.status_code == 201
        
        # List all persons
        response = client.get("/persons")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        # Verify names
        names = [p["name"] for p in data]
        assert "Alice" in names
        assert "Bob" in names
        assert "Charlie" in names
    
    def test_delete_one_person_others_remain(self, client):
        """Test that deleting one person doesn't affect others"""
        # Create three persons
        client.post("/persons", json={"name": "Alice", "age": 25, "email": "alice@example.com"})
        response_bob = client.post("/persons", json={"name": "Bob", "age": 35, "email": "bob@example.com"})
        client.post("/persons", json={"name": "Charlie", "age": 45, "email": "charlie@example.com"})
        
        bob_id = response_bob.json()["id"]
        
        # Delete Bob
        client.delete(f"/persons/{bob_id}")
        
        # Verify Alice and Charlie still exist
        all_persons = client.get("/persons").json()
        assert len(all_persons) == 2
        names = [p["name"] for p in all_persons]
        assert "Alice" in names
        assert "Charlie" in names
        assert "Bob" not in names
