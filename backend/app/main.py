import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import initialise_database, storage_diagnostics
from app.routers import complaints, outages

@asynccontextmanager
async def lifespan(_: FastAPI):
    initialise_database()
    yield

app = FastAPI(title="GRAMCONNECT API", version="1.0.0", lifespan=lifespan)
origins = [item.strip() for item in os.getenv("FRONTEND_ORIGIN", "http://localhost:3000").split(",") if item.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["GET", "POST", "PATCH"], allow_headers=["Content-Type", "Authorization"])

@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "service": "gramconnect-backend", **storage_diagnostics()}

app.include_router(complaints.router, prefix="/api")
app.include_router(outages.router, prefix="/api")
