# Demo FastAPI Backend

A simple REST API built with FastAPI, SQLite demo database, and comprehensive tests.

## Setup

`ash
pip install -r requirements.txt
`

## Run the API

`ash
uvicorn app.main:app --reload
`

API will be available at http://localhost:8000  
Docs at http://localhost:8000/docs

## Run Tests

`ash
pytest -v
`

## Endpoints

- GET / - Root
- GET /health - Health check
- GET /items - List all items
- GET /items/{id} - Get item by ID
- POST /items - Create new item
- DELETE /items/{id} - Delete item
"# Tp_cicd" 
