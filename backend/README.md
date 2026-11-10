# GRAMCONNECT backend

The backend is a FastAPI service that owns the complaint, resident, outage and audit data. It uses SQLite locally so it can be demonstrated without credentials. The API is designed to be swapped to Supabase/Postgres during production deployment.

## Run locally

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs` to show the documented API. The health endpoint is `GET /health`.

## Folder guide

- `app/main.py` starts FastAPI and configures CORS.
- `app/database.py` creates local tables and provides database connections.
- `app/schemas.py` validates request/response data.
- `app/services/` contains business rules, such as deterministic classification and routing.
- `app/routers/` contains resource-specific HTTP endpoints.

## Safety boundary

This local backend stores data in `data/gramconnect.db`. It does not transmit complaints to WhatsApp, Spandana/PGRS, DISCOMs, SMS providers, or any authority. Production adapters must be approved and configured with server-side environment secrets.
