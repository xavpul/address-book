## 📒 Address Book API

A small FastAPI app with async SQLAlchemy + SQLite and Haversine-based “nearby” search.

---

## 🚀 Features
- CRUD for addresses (name, lat, lng)
- Nearby search by radius (Haversine)
- Async SQLAlchemy 2.0 + aiosqlite
- Alembic migrations
- OpenAPI docs at /docs

---

## 🧰 Requirements
- Python 3.13+
- uv (package manager): https://docs.astral.sh/uv/

---

## 🔧 Setup
1) Install dependencies
   uv sync

2) Environment (create .env)
   DB_URL=sqlite+aiosqlite:///./app.db
   DB_MIGRATION_URL=sqlite:///./app.db

3) Migrate database
   uv run alembic upgrade head

4) Run the server
   uv run uvicorn main:app --reload

Open: http://127.0.0.1:8000/docs

---

## 🧪 Testing
Install dev deps and run tests:
```
uv add --dev pytest pytest-asyncio httpx anyio
uv run pytest -q
```

---

## 📡 API Quickstart (curl)
Create:
```
curl -X POST http://127.0.0.1:8000/addresses/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Home","lat":40.7128,"lng":-74.0060}'
```

Get by ID:
```
curl http://127.0.0.1:8000/addresses/1
```

Nearby (2 km around a point):
```
curl "http://127.0.0.1:8000/addresses/nearby?lat=40.7128&lng=-74.0060&radius_km=2"
```

---

## 📄 License
MIT address-book
