#!/bin/bash

API_URL="http://127.0.0.1:8001"

echo "=== Testing Person API with PostgreSQL ==="
echo ""

# Create persons
echo "1. Creating persons..."
echo ""

echo "Creating Alice:"
curl -s -X POST "$API_URL/persons" \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice Smith","age":25,"email":"alice@example.com"}' | jq
echo ""

echo "Creating Bob:"
curl -s -X POST "$API_URL/persons" \
  -H "Content-Type: application/json" \
  -d '{"name":"Bob Johnson","age":30,"email":"bob@example.com"}' | jq
echo ""

echo "Creating Charlie:"
curl -s -X POST "$API_URL/persons" \
  -H "Content-Type: application/json" \
  -d '{"name":"Charlie Brown","age":35,"email":"charlie@example.com"}' | jq
echo ""

# Get all persons
echo "2. Getting all persons..."
curl -s "$API_URL/persons" | jq
echo ""

# Get specific person
echo "3. Getting person with ID 1..."
curl -s "$API_URL/persons/1" | jq
echo ""

# Update person
echo "4. Updating person with ID 1..."
curl -s -X PUT "$API_URL/persons/1" \
  -H "Content-Type: application/json" \
  -d '{"age":26}' | jq
echo ""

# Try to create duplicate email
echo "5. Testing email uniqueness (should fail)..."
curl -s -X POST "$API_URL/persons" \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice Clone","age":28,"email":"alice@example.com"}' | jq
echo ""

# Delete person
echo "6. Deleting person with ID 2..."
curl -s -X DELETE "$API_URL/persons/2" -w "Status: %{http_code}\n"
echo ""

# Get all persons after delete
echo "7. Getting all persons after delete..."
curl -s "$API_URL/persons" | jq
echo ""

echo "=== Test Complete ==="
