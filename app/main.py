import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_

from . import models, schemas
from .database import engine, get_db, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Support CRM API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


def generate_ticket_id(db: Session) -> str:
    """Generates the next sequential ticket id, e.g. TKT-001, TKT-002, ..."""
    count = db.query(models.Ticket).count()
    next_num = count + 1
    # Guard against collisions if tickets were ever deleted
    while db.query(models.Ticket).filter(
        models.Ticket.ticket_id == f"TKT-{next_num:03d}"
    ).first():
        next_num += 1
    return f"TKT-{next_num:03d}"



@app.post("/api/tickets", response_model=schemas.TicketCreateOut)
def create_ticket(payload: schemas.TicketCreate, db: Session = Depends(get_db)):
    ticket_id = generate_ticket_id(db)
    ticket = models.Ticket(
        ticket_id=ticket_id,
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        subject=payload.subject,
        description=payload.description,
        status="Open",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return schemas.TicketCreateOut(ticket_id=ticket.ticket_id, created_at=ticket.created_at)


@app.get("/api/tickets", response_model=list[schemas.TicketListOut])
def list_tickets(
    status: Optional[str] = Query(None, description="Filter by status: Open, In Progress, Closed"),
    search: Optional[str] = Query(None, description="Search across name, id, email, description"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Ticket)

    if status:
        query = query.filter(models.Ticket.status == status)

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                models.Ticket.customer_name.ilike(like),
                models.Ticket.ticket_id.ilike(like),
                models.Ticket.customer_email.ilike(like),
                models.Ticket.subject.ilike(like),
                models.Ticket.description.ilike(like),
            )
        )

    tickets = query.order_by(models.Ticket.created_at.desc()).all()
    return tickets


@app.get("/api/tickets/{ticket_id}", response_model=schemas.TicketDetailOut)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.put("/api/tickets/{ticket_id}", response_model=schemas.TicketUpdateOut)
def update_ticket(ticket_id: str, payload: schemas.TicketUpdate, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    valid_statuses = {"Open", "In Progress", "Closed"}
    if payload.status is not None:
        if payload.status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of {valid_statuses}",
            )
        ticket.status = payload.status

    if payload.notes:
        note = models.Note(ticket_id=ticket.ticket_id, note_text=payload.notes)
        db.add(note)

    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    return schemas.TicketUpdateOut(success=True, updated_at=ticket.updated_at)


@app.delete("/api/tickets/{ticket_id}")
def delete_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db.delete(ticket)
    db.commit()
    return {"success": True}



@app.get("/")
def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/ticket.html")
def serve_ticket_page():
    return FileResponse(os.path.join(STATIC_DIR, "ticket.html"))


app.mount("/", StaticFiles(directory=STATIC_DIR), name="static")
