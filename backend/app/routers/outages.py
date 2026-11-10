from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from app.database import as_dict, connection, supabase_client, using_supabase
from app.schemas import OutageCreate, OutageUpdate
from app.services.rules import entity_id, reference

router = APIRouter(tags=["outages"])

@router.get("/outages")
def list_outages():
    if using_supabase():
        return supabase_client().table("outage_alerts").select("*").order("created_at", desc=True).execute().data
    with connection() as db:
        return [as_dict(row) for row in db.execute("SELECT * FROM outage_alerts ORDER BY created_at DESC").fetchall()]

@router.post("/outages", status_code=status.HTTP_201_CREATED)
def create_outage(payload: OutageCreate):
    outage_id, outage_ref = entity_id(), reference("OUT")
    if using_supabase():
        data = {"id": outage_id, "reference_id": outage_ref, "locality": payload.locality, "source": payload.source, "details": payload.details, "status": "Draft", "restoration_estimate": payload.restoration_estimate}
        return supabase_client().table("outage_alerts").insert(data).execute().data[0]
    with connection() as db:
        db.execute("INSERT INTO outage_alerts (id, reference_id, locality, source, details, status, restoration_estimate) VALUES (?, ?, ?, ?, ?, 'Draft', ?)", (outage_id, outage_ref, payload.locality, payload.source, payload.details, payload.restoration_estimate))
        return as_dict(db.execute("SELECT * FROM outage_alerts WHERE id = ?", (outage_id,)).fetchone())

@router.patch("/outages/{outage_id}")
def update_outage(outage_id: str, payload: OutageUpdate):
    if using_supabase():
        client = supabase_client()
        records = client.table("outage_alerts").select("*").eq("id", outage_id).execute().data
        if not records: raise HTTPException(404, "Outage alert not found")
        current = records[0]
        if payload.status == "Sent" and current["status"] != "Verified": raise HTTPException(409, "An outage must be verified before notification dispatch.")
        data = {"status": payload.status}
        if payload.status == "Verified": data["verified_at"] = datetime.now(timezone.utc).isoformat()
        return client.table("outage_alerts").update(data).eq("id", outage_id).execute().data[0]
    with connection() as db:
        current = db.execute("SELECT * FROM outage_alerts WHERE id = ?", (outage_id,)).fetchone()
        if not current: raise HTTPException(404, "Outage alert not found")
        if payload.status == "Sent" and current["status"] != "Verified":
            raise HTTPException(409, "An outage must be verified before notification dispatch.")
        verified_at = datetime.now(timezone.utc).isoformat() if payload.status == "Verified" else current["verified_at"]
        db.execute("UPDATE outage_alerts SET status = ?, verified_at = ? WHERE id = ?", (payload.status, verified_at, outage_id))
        return as_dict(db.execute("SELECT * FROM outage_alerts WHERE id = ?", (outage_id,)).fetchone())
