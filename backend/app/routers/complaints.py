import json
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from app.database import as_dict, connection
from app.schemas import ComplaintCreate, ComplaintUpdate, ResidentCreate
from app.services.rules import ROUTES, classify_issue, priority_for, reference

router = APIRouter(tags=["complaints"])

@router.post("/residents", status_code=status.HTTP_201_CREATED)
def create_resident(payload: ResidentCreate):
    resident_id = reference("RES")
    with connection() as db:
        db.execute("INSERT INTO residents (id, full_name, phone_hint, locality, preferred_language, notification_channels, consent_recorded) VALUES (?, ?, ?, ?, ?, ?, ?)", (resident_id, payload.full_name, payload.phone_hint, payload.locality, payload.preferred_language, json.dumps(payload.notification_channels), int(payload.consent_recorded)))
        return as_dict(db.execute("SELECT * FROM residents WHERE id = ?", (resident_id,)).fetchone())

@router.get("/complaints")
def list_complaints():
    with connection() as db:
        return [as_dict(row) for row in db.execute("SELECT * FROM complaints ORDER BY submitted_at DESC").fetchall()]

@router.post("/complaints", status_code=status.HTTP_201_CREATED)
def create_complaint(payload: ComplaintCreate):
    category = payload.category or classify_issue(payload.description)
    complaint_id, complaint_ref = reference("CASE"), reference("GC")
    with connection() as db:
        db.execute("INSERT INTO complaints (id, reference_id, resident_id, category, description, locality, landmark, priority, status, department) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Submitted', ?)", (complaint_id, complaint_ref, payload.resident_id, category, payload.description, payload.locality, payload.landmark, priority_for(category), ROUTES[category]))
        db.execute("INSERT INTO complaint_events (complaint_id, actor_name, event_type, event_detail) VALUES (?, 'Rules engine', 'created', ?)", (complaint_id, f"Classified as {category}; queued for human review."))
        return as_dict(db.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,)).fetchone())

@router.get("/complaints/{complaint_id}/events")
def complaint_events(complaint_id: str):
    with connection() as db:
        rows = db.execute("SELECT * FROM complaint_events WHERE complaint_id = ? ORDER BY created_at", (complaint_id,)).fetchall()
        return [as_dict(row) for row in rows]

@router.patch("/complaints/{complaint_id}")
def update_complaint(complaint_id: str, payload: ComplaintUpdate):
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
