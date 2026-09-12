"""Optional demo data: run `python seed_demo.py` after the app has initialized."""
from datetime import datetime, timedelta

from app.database import Base, SessionLocal, engine
from app.models import Appointment, Patient, Role, User
from app.security import hash_password

Base.metadata.create_all(engine)
db = SessionLocal()
try:
    doctor = db.query(User).filter_by(email="doctor@roshsoft.local").first()
    if not doctor:
        doctor = User(full_name="Dr Demo Physician", email="doctor@roshsoft.local",
                      password_hash=hash_password("ChangeMe123!"), role=Role.DOCTOR)
        db.add(doctor); db.flush()
    patient = db.query(Patient).filter_by(patient_number="RSC-DEMO-0001").first()
    if not patient:
        patient = Patient(patient_number="RSC-DEMO-0001", full_name="Demo Patient", phone="9000000000",
                          blood_group="O+", allergies="Penicillin (demo)", consent_given=True)
        db.add(patient); db.flush()
        db.add(Appointment(patient_id=patient.id, doctor_id=doctor.id,
                           scheduled_at=datetime.now() + timedelta(days=1), reason="Demo health review"))
    db.commit()
    print("Demo data ready. Doctor login: doctor@roshsoft.local / ChangeMe123!")
finally:
    db.close()

