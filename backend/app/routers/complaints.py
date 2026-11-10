import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from app.security import require_admin
from app.database import as_dict, connection, supabase_client, using_supabase
from app.schemas import ComplaintCreate, ComplaintUpdate, ResidentCreate
from app.services.rules import ROUTES, classify_issue, entity_id, priority_for, reference

router = APIRouter(tags=["complaints"])

@router.get("/residents", dependencies=[Depends(require_admin)])
def list_residents():
    if using_supabase():
        return supabase_client().table("residents").select("*").order("created_at", desc=True).execute().data
    with connection() as db:
        return [as_dict(row) for row in db.execute("SELECT * FROM residents ORDER BY created_at DESC").fetchall()]

@router.post("/residents", status_code=status.HTTP_201_CREATED)
def create_resident(payload: ResidentCreate):
    resident_id = entity_id()
    if using_supabase():
        data = {"id": resident_id, "full_name": payload.full_name, "phone_hint": payload.phone_hint, "locality": payload.locality, "preferred_language": payload.preferred_language, "notification_channels": payload.notification_channels, "consent_recorded": payload.consent_recorded}
        return supabase_client().table("residents").insert(data).execute().data[0]
    with connection() as db:
        db.execute("INSERT INTO residents (id, full_name, phone_hint, locality, preferred_language, notification_channels, consent_recorded) VALUES (?, ?, ?, ?, ?, ?, ?)", (resident_id, payload.full_name, payload.phone_hint, payload.locality, payload.preferred_language, json.dumps(payload.notification_channels), int(payload.consent_recorded)))
        return as_dict(db.execute("SELECT * FROM residents WHERE id = ?", (resident_id,)).fetchone())

@router.get("/complaints", dependencies=[Depends(require_admin)])
def list_complaints():
    if using_supabase():
        return supabase_client().table("complaints").select("*").order("submitted_at", desc=True).execute().data
    with connection() as db:
        return [as_dict(row) for row in db.execute("SELECT * FROM complaints ORDER BY submitted_at DESC").fetchall()]

@router.post("/complaints", status_code=status.HTTP_201_CREATED)
def create_complaint(payload: ComplaintCreate):
    category = payload.category or classify_issue(payload.description)
    complaint_id, complaint_ref = entity_id(), reference("GC")
    if using_supabase():
        client = supabase_client()
        data = {"id": complaint_id, "reference_id": complaint_ref, "resident_id": payload.resident_id, "category": category, "description": payload.description, "locality": payload.locality, "landmark": payload.landmark, "priority": priority_for(category), "status": "Submitted", "department": ROUTES[category]}
        created = client.table("complaints").insert(data).execute().data[0]
        client.table("complaint_events").insert({"complaint_id": complaint_id, "actor_name": "Rules engine", "event_type": "created", "event_detail": f"Classified as {category}; queued for human review."}).execute()
        return created
    with connection() as db:
        db.execute("INSERT INTO complaints (id, reference_id, resident_id, category, description, locality, landmark, priority, status, department) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Submitted', ?)", (complaint_id, complaint_ref, payload.resident_id, category, payload.description, payload.locality, payload.landmark, priority_for(category), ROUTES[category]))
        db.execute("INSERT INTO complaint_events (complaint_id, actor_name, event_type, event_detail) VALUES (?, 'Rules engine', 'created', ?)", (complaint_id, f"Classified as {category}; queued for human review."))
        return as_dict(db.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,)).fetchone())

@router.get("/complaints/{complaint_id}/events", dependencies=[Depends(require_admin)])
def complaint_events(complaint_id: str):
    if using_supabase():
        return supabase_client().table("complaint_events").select("*").eq("complaint_id", complaint_id).order("created_at").execute().data
    with connection() as db:
        rows = db.execute("SELECT * FROM complaint_events WHERE complaint_id = ? ORDER BY created_at", (complaint_id,)).fetchall()
        return [as_dict(row) for row in rows]

@router.patch("/complaints/{complaint_id}", dependencies=[Depends(require_admin)])
def update_complaint(complaint_id: str, payload: ComplaintUpdate):
    if using_supabase():
        client = supabase_client()
        current = client.table("complaints").select("id").eq("id", complaint_id).execute().data
        if not current: raise HTTPException(404, "Complaint not found")
        data = {k: v for k, v in {"status": payload.status, "department": payload.department, "authority_reference": payload.authority_reference, "updated_at": datetime.now(timezone.utc).isoformat()}.items() if v is not None}
        updated = client.table("complaints").update(data).eq("id", complaint_id).execute().data[0]
        client.table("complaint_events").insert({"complaint_id": complaint_id, "actor_name": "Administrator", "event_type": "updated", "event_detail": payload.note}).execute()
        return updated
    with connection() as db:
        current = db.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,)).fetchone()
        if not current: raise HTTPException(404, "Complaint not found")
        changes, params = [], []
        for column, value in (("status", payload.status), ("department", payload.department), ("authority_reference", payload.authority_reference)):
            if value is not None: changes.append(f"{column} = ?"); params.append(value)
        if changes:
            params.extend([datetime.now(timezone.utc).isoformat(), complaint_id])
            db.execute(f"UPDATE complaints SET {', '.join(changes)}, updated_at = ? WHERE id = ?", params)
        db.execute("INSERT INTO complaint_events (complaint_id, actor_name, event_type, event_detail) VALUES (?, 'Administrator', 'updated', ?)", (complaint_id, payload.note))
        return as_dict(db.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,)).fetchone())
