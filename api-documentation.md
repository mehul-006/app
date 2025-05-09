# API Documentation

This document provides detailed information about the REST API endpoints exposed by the Flask PostgreSQL application.

## Base URL

All API endpoints are relative to the base URL:

```
https://app.example.com
```

## Authentication

Currently, the API does not implement authentication. If implementing in production, consider adding authentication mechanisms like API keys, OAuth, or JWT tokens.

## API Endpoints

### Health Check

Used by Kubernetes for health probing and general availability testing.

**Request:**
```
GET /healthz
```

**Response:**
```json
{
  "status": "healthy"
}
```

**Status Codes:**
- `200 OK` - Service is healthy and operational

---

### Get Data

Retrieves all records from the test_table in the PostgreSQL database.

**Request:**
```
GET /api/data
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Initial Record",
      "created_at": "2025-05-09T15:30:45.123456"
    },
    {
      "id": 2,
      "name": "Test Record",
      "created_at": "2025-05-09T16:12:33.654321"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Request successful
- `500 Internal Server Error` - Database error occurred

**Error Response:**
```json
{
  "error": "Error message details"
}
```

---

### Setup Database

Initializes the database schema by creating necessary tables and adding initial data if needed.

**Request:**
```
GET /api/setup
```

**Response:**
```json
{
  "status": "Database setup successful"
}
```

**Status Codes:**
- `200 OK` - Setup completed successfully
- `500 Internal Server Error` - Setup failed

**Error Response:**
```json
{
  "error": "Error message details"
}
```

## Data Models

### Test Table

Represents the basic data structure stored in PostgreSQL.

| Field | Type | Description |
|-------|------|-------------|
| id | SERIAL | Primary key, auto-incrementing identifier |
| name | VARCHAR(100) | Name or description |
| created_at | TIMESTAMP | Creation timestamp (defaults to current time) |

## Error Handling

All API endpoints use the following error response format:

```json
{
  "error": "Description of what went wrong"
}
```

Common error scenarios:

1. Database connection failure
2. Query execution errors
3. Invalid input parameters (for extended implementations)

## Rate Limiting

Currently, there is no rate limiting implemented. For production deployments, consider adding rate limiting using tools like Flask-Limiter or a proxy like NGINX.

## Extending the API

To extend the API with additional functionality, add new endpoints to the `app.py` file. Examples of extensions might include:

### Adding a POST endpoint

```python
@app.route('/api/data', methods=['POST'])
def add_data():
    try:
        data = request.get_json()
        name = data.get('name')
        
        if not name:
            return jsonify({"error": "Name is required"}), 400
            
        conn = connect_to_postgres()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            "INSERT INTO test_table (name) VALUES (%s) RETURNING *;", 
            (name,)
        )
        new_record = cursor.fetchone()
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"data": new_record}), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Adding a PUT endpoint

```python
@app.route('/api/data/<int:id>', methods=['PUT'])
def update_data(id):
    try:
        data = request.get_json()
        name = data.get('name')
        
        if not name:
            return jsonify({"error": "Name is required"}), 400
            
        conn = connect_to_postgres()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            "UPDATE test_table SET name = %s WHERE id = %s RETURNING *;", 
            (name, id)
        )
        updated_record = cursor.fetchone()
        conn.commit()
        
        cursor.close()
        conn.close()
        
        if not updated_record:
            return jsonify({"error": "Record not found"}), 404
            
        return jsonify({"data": updated_record})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Adding a DELETE endpoint

```python
@app.route('/api/data/<int:id>', methods=['DELETE'])
def delete_data(id):
    try:
        conn = connect_to_postgres()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM test_table WHERE id = %s RETURNING id;", (id,))
        deleted = cursor.fetchone()
        conn.commit()
        
        cursor.close()
        conn.close()
        
        if not deleted:
            return jsonify({"error": "Record not found"}), 404
            
        return jsonify({"status": "Record deleted", "id": deleted[0]})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

## Testing the API

You can test the API endpoints using curl:

```bash
# Health check
curl -k https://app.example.com/healthz

# Get data
curl -k https://app.example.com/api/data

# Setup database
curl -k https://app.example.com/api/setup
```

For more complex testing, consider using tools like Postman or writing automated tests with pytest.
