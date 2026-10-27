from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from pathlib import Path

app = FastAPI(title="Demo API", version="1.0.0")

DB_PATH = Path(__file__).parent.parent / "data" / "demo.db"

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    class Config:
        from_attributes = True

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')
    cur.execute("SELECT COUNT(*) as c FROM items")
    row = cur.fetchone()
    count = row['c'] if row else 0
    if count == 0:
        cur.execute("INSERT INTO items (name, description) VALUES ('Demo Item', 'This is a demo item')")
        cur.execute("INSERT INTO items (name, description) VALUES ('Sample Product', 'A sample product')")
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def root():
    return {"message": "Welcome to Demo API", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/items", response_model=List[Item])
def list_items(db: sqlite3.Connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT id, name, description FROM items")
    rows = cur.fetchall()
    return [{"id": row["id"], "name": row["name"], "description": row["description"]} for row in rows]

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int, db: sqlite3.Connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT id, name, description FROM items WHERE id = ?", (item_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": row["id"], "name": row["name"], "description": row["description"]}

@app.post("/items", response_model=Item, status_code=201)
def create_item(item: ItemCreate, db: sqlite3.Connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("INSERT INTO items (name, description) VALUES (?, ?)", (item.name, item.description))
    db.commit()
    item_id = cur.lastrowid
    cur.execute("SELECT id, name, description FROM items WHERE id = ?", (item_id,))
    row = cur.fetchone()
    return {"id": row["id"], "name": row["name"], "description": row["description"]}

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: sqlite3.Connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("DELETE FROM items WHERE id = ?", (item_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    db.commit()
    return None
