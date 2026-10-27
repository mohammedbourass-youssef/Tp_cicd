from fastapi.testclient import TestClient
from app.main import app, DB_PATH, init_db
import os
import tempfile

client = TestClient(app)

def setup_module():
    # Use fresh test db
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_list_items():
    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

def test_get_item():
    response = client.get("/items/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "name" in data

def test_get_item_not_found():
    response = client.get("/items/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_create_item():
    response = client.post("/items", json={"name": "Test Item", "description": "Created in test"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert "id" in data

def test_delete_item():
    # Create item first
    create_resp = client.post("/items", json={"name": "ToDelete", "description": "temp"})
    item_id = create_resp.json()["id"]
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 204
    # Verify deleted
    get_resp = client.get(f"/items/{item_id}")
    assert get_resp.status_code == 404

def test_delete_item_not_found():
    response = client.delete("/items/99999")
    assert response.status_code == 404
