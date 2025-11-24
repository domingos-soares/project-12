# Person API - FastAPI Server

A REST API server built with FastAPI that manages Person objects with full CRUD operations using PostgreSQL database.

## Features

- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ Automatic API documentation (Swagger UI)
- ✅ Email uniqueness validation
- ✅ Docker Compose for easy database setup

## Prerequisites

- Python 3.8+
- PostgreSQL (or Docker for containerized database)

## Setup

### 1. Install Dependencies

Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start PostgreSQL Database

**Option A: Using Docker Compose (Recommended)**

```bash
docker-compose up -d
```

This will start a PostgreSQL container on port 5432.

**Option B: Using Local PostgreSQL**

Install PostgreSQL locally and create a database:

```sql
CREATE DATABASE persons_db;
```

### 3. Configure Environment

The `.env` file is already created with default settings:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/persons_db
```

Update this if you're using different credentials.

### 4. Run the Server

```bash
source venv/bin/activate
uvicorn main:app --reload
```

The server will start at `http://127.0.0.1:8000`

Database tables will be created automatically on first run.

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## API Endpoints

### GET /persons
Get all persons

### GET /persons/{person_id}
Get a specific person by ID

### POST /persons
Create a new person

**Request Body:**
```json
{
  "name": "John Doe",
  "age": 30,
  "email": "john@example.com"
}
```

### PUT /persons/{person_id}
Update an existing person (partial updates supported)

**Request Body:**
```json
{
  "name": "Jane Doe",
  "age": 31
}
```

### DELETE /persons/{person_id}
Delete a person

## Database Schema

The `persons` table includes:
- `id` (integer, primary key, auto-increment)
- `name` (string, required)
- `age` (integer, required)
- `email` (string, required, unique)

## Testing

### Automated Test Script

Run the included test script to test all API endpoints:

```bash
./test_api.sh
```

This script will:
- Create multiple persons
- Retrieve all persons
- Get a specific person
- Update a person
- Test email uniqueness validation
- Delete a person

### Manual Testing Examples

```bash
# Create a person
curl -X POST "http://127.0.0.1:8001/persons" \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","age":25,"email":"alice@example.com"}'

# Get all persons
curl "http://127.0.0.1:8001/persons"

# Get a specific person
curl "http://127.0.0.1:8001/persons/1"

# Update a person
curl -X PUT "http://127.0.0.1:8001/persons/1" \
  -H "Content-Type: application/json" \
  -d '{"age":26}'

# Delete a person
curl -X DELETE "http://127.0.0.1:8001/persons/1"
```

## Database Management

### View all persons in database

```bash
psql -d persons_db -c "SELECT * FROM persons;"
```

### Reset database

```bash
psql -d persons_db -c "TRUNCATE TABLE persons RESTART IDENTITY;"
```

### Drop and recreate database

```bash
dropdb persons_db
createdb persons_db
# Restart the server to recreate tables
```
