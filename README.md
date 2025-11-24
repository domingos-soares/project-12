# Person API - FastAPI Server

A REST API server built with FastAPI that manages Person objects with full CRUD operations.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Server

Start the server with:

```bash
uvicorn main:app --reload
```

The server will start at `http://127.0.0.1:8000`

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

## Example Usage

```bash
# Create a person
curl -X POST "http://127.0.0.1:8000/persons" \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","age":25,"email":"alice@example.com"}'

# Get all persons
curl "http://127.0.0.1:8000/persons"

# Get a specific person
curl "http://127.0.0.1:8000/persons/1"

# Update a person
curl -X PUT "http://127.0.0.1:8000/persons/1" \
  -H "Content-Type: application/json" \
  -d '{"age":26}'

# Delete a person
curl -X DELETE "http://127.0.0.1:8000/persons/1"
```
