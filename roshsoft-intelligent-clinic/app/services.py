from datetime import datetime
from sqlalchemy.orm import Session

from .models import AuditLog, Patient


def audit(db: Session, actor_id: int | None, action: str, entity_type: str,
          entity_id: str | None = None, detail: str | None = None,
          ip_address: str | None = None) -> None:
    db.add(AuditLog(actor_id=actor_id, action=action, entity_type=entity_type,
                    entity_id=entity_id, detail=detail, ip_address=ip_address))


def patient_number(db: Session) -> str:
    year = datetime.utcnow().year
    count = db.query(Patient).count() + 1
    return f"RSC-{year}-{count:05d}"


def clinical_support(patient: Patient, symptoms: str, vitals: str) -> str:
    """Transparent rules-only decision support; never a diagnosis engine."""
    notes: list[str] = []
    combined = f"{symptoms} {vitals}".lower()
    red_flags = {
        "chest pain": "Chest pain recorded—perform immediate clinical triage.",
        "difficulty breathing": "Breathing difficulty recorded—assess oxygenation and urgency.",
        "unconscious": "Altered consciousness recorded—activate emergency protocol.",
        "severe bleeding": "Severe bleeding recorded—activate emergency protocol.",
    }
    for phrase, message in red_flags.items():
        if phrase in combined:
            notes.append(f"URGENT: {message}")
    if patient.allergies:
        notes.append(f"Verify against recorded allergies: {patient.allergies}")
    if patient.current_medications:
        notes.append("Reconcile medicines and check interactions before prescribing.")
    if not notes:
        notes.append("No configured red-flag phrase detected; complete normal clinical assessment.")
    notes.append("Decision support only. The treating doctor must verify all information and decide care.")
    return "\n".join(notes)

