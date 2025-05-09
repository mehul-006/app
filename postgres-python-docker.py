# app.py
import os
import time
import json
from flask import Flask, jsonify
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

def connect_to_postgres():
    """Connect to PostgreSQL database with retries"""
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=os.environ.get("DB_HOST", "postgres"),
                database=os.environ.get("DB_NAME", "postgres"),
                user=os.environ.get("DB_USER", "postgres"),
                password=os.environ.get("DB_PASSWORD", "postgres"),
                port=os.environ.get("DB_PORT", "5432")
            )
            print("Connection to PostgreSQL successful!")
            return conn
        except OperationalError as e:
            retries -= 1
            print(f"Error connecting to PostgreSQL: {e}")
            print(f"Retries left: {retries}")
            time.sleep(5)
    
    raise Exception("Failed to connect to PostgreSQL after multiple attempts")

@app.route('/healthz')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/api/data')
def get_data():
    """API endpoint to fetch data from PostgreSQL"""
    try:
        conn = connect_to_postgres()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query the table
        cursor.execute("SELECT * FROM test_table ORDER BY id;")
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({"data": rows})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/setup')
def setup_db():
    """API endpoint to set up the database"""
    try:
        conn = connect_to_postgres()
        cursor = conn.cursor()
        
        # Create a test table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        
        # Insert a test record if table is empty
        cursor.execute("SELECT COUNT(*) FROM test_table;")
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.execute("INSERT INTO test_table (name) VALUES ('Initial Record');")
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"status": "Database setup successful"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting the Flask application...")
    # Call setup_db at startup
    try:
        setup_db()
        print("Database setup completed successfully")
    except Exception as e:
        print(f"Database setup error: {e}")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)


# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]


# requirements.txt
psycopg2-binary==2.9.6
flask==2.3.3
gunicorn==21.2.0


# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    depends_on:
      - postgres

  app:
    build: .
    environment:
      DB_HOST: postgres
      DB_NAME: postgres
      DB_USER: postgres
      DB_PASSWORD: postgres
      DB_PORT: 5432
    depends_on:
      - postgres

volumes:
  postgres_data:
