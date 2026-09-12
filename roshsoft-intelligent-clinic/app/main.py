from datetime import date, datetime
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .database import Base, SessionLocal, engine, get_db
from .models import Appointment, AppointmentStatus, Consultation, Invoice, Patient, Prescription, Role, User
from .security import hash_password, verify_password
from .services import audit, clinical_support, patient_number

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title=settings.app_name, docs_url="/api/docs")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, https_only=settings.session_https_only,
                   same_site="lax", max_age=8 * 60 * 60)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        if not db.query(User).first():
            db.add(User(full_name="Clinic Administrator", email="admin@roshsoft.local",
                        password_hash=hash_password("ChangeMe123!"), role=Role.ADMIN))
            db.commit()
    finally:
        db.close()


def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    user = db.get(User, user_id) if user_id else None
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    return user


def page(request: Request, name: str, user: User | None = None, **context):
    return templates.TemplateResponse(request, name, {"user": user, "clinic_name": settings.clinic_name, **context})


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return page(request, "login.html")


@app.post("/login")
def login(request: Request, email: Annotated[str, Form()], password: Annotated[str, Form()], db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == email.strip().lower()).first()
    if not user or not verify_password(password, user.password_hash):
        return page(request, "login.html", error="Invalid email or password.")
    request.session.clear()
    request.session["user_id"] = user.id
    audit(db, user.id, "login", "session", ip_address=request.client.host if request.client else None)
    db.commit()
    return RedirectResponse("/", status_code=303)


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)):
    today = date.today()
    appointments = (db.query(Appointment).options(joinedload(Appointment.patient), joinedload(Appointment.doctor))
                    .filter(func.date(Appointment.scheduled_at) == today).order_by(Appointment.scheduled_at).all())
    stats = {"patients": db.query(Patient).count(), "today": len(appointments),
             "waiting": sum(a.status in (AppointmentStatus.BOOKED, AppointmentStatus.CHECKED_IN) for a in appointments),
             "completed": sum(a.status == AppointmentStatus.COMPLETED for a in appointments)}
    return page(request, "dashboard.html", user, appointments=appointments, stats=stats)


@app.get("/patients", response_class=HTMLResponse)
def patients(request: Request, q: str = "", db: Session = Depends(get_db), user: User = Depends(current_user)):
    query = db.query(Patient)
    if q.strip():
        term = f"%{q.strip()}%"
        query = query.filter(or_(Patient.full_name.ilike(term), Patient.phone.ilike(term), Patient.patient_number.ilike(term)))
    return page(request, "patients.html", user, patients=query.order_by(Patient.created_at.desc()).all(), q=q)


@app.get("/patients/new", response_class=HTMLResponse)
def new_patient(request: Request, user: User = Depends(current_user)):
    return page(request, "patient_form.html", user)


@app.post("/patients/new")
def create_patient(request: Request, full_name: Annotated[str, Form()], phone: Annotated[str, Form()],
                   date_of_birth: Annotated[str, Form()] = "", sex: Annotated[str, Form()] = "",
                   email: Annotated[str, Form()] = "", address: Annotated[str, Form()] = "",
                   blood_group: Annotated[str, Form()] = "", allergies: Annotated[str, Form()] = "",
                   chronic_conditions: Annotated[str, Form()] = "", current_medications: Annotated[str, Form()] = "",
                   emergency_contact: Annotated[str, Form()] = "", consent_given: Annotated[str | None, Form()] = None,
                   db: Session = Depends(get_db), user: User = Depends(current_user)):
    patient = Patient(patient_number=patient_number(db), full_name=full_name.strip(), phone=phone.strip(),
                      date_of_birth=date.fromisoformat(date_of_birth) if date_of_birth else None, sex=sex or None,
                      email=email or None, address=address or None, blood_group=blood_group or None,
                      allergies=allergies or None, chronic_conditions=chronic_conditions or None,
                      current_medications=current_medications or None, emergency_contact=emergency_contact or None,
                      consent_given=consent_given == "on")
    db.add(patient); db.flush()
    audit(db, user.id, "create", "patient", str(patient.id), "New patient registered", request.client.host if request.client else None)
    db.commit()
    return RedirectResponse(f"/patients/{patient.id}", status_code=303)


@app.get("/patients/{patient_id}", response_class=HTMLResponse)
def patient_detail(patient_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)):
    patient = (db.query(Patient).options(joinedload(Patient.appointments).joinedload(Appointment.doctor),
                                        joinedload(Patient.appointments).joinedload(Appointment.consultation))
               .filter(Patient.id == patient_id).first())
    if not patient: raise HTTPException(404)
    audit(db, user.id, "view", "patient", str(patient.id), ip_address=request.client.host if request.client else None); db.commit()
    return page(request, "patient_detail.html", user, patient=patient,
                appointments=sorted(patient.appointments, key=lambda a: a.scheduled_at, reverse=True))


@app.get("/appointments/new", response_class=HTMLResponse)
def new_appointment(request: Request, patient_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    return page(request, "appointment_form.html", user, patients=db.query(Patient).order_by(Patient.full_name).all(),
                doctors=db.query(User).filter(User.role.in_([Role.DOCTOR, Role.ADMIN]), User.is_active.is_(True)).all(), patient_id=patient_id)


@app.post("/appointments/new")
def create_appointment(request: Request, patient_id: Annotated[int, Form()], doctor_id: Annotated[int, Form()],
                       scheduled_at: Annotated[str, Form()], reason: Annotated[str, Form()],
                       db: Session = Depends(get_db), user: User = Depends(current_user)):
    appointment = Appointment(patient_id=patient_id, doctor_id=doctor_id,
                              scheduled_at=datetime.fromisoformat(scheduled_at), reason=reason.strip())
    db.add(appointment); db.flush()
    audit(db, user.id, "create", "appointment", str(appointment.id), f"Scheduled {scheduled_at}", request.client.host if request.client else None)
    db.commit()
    return RedirectResponse(f"/appointments/{appointment.id}", status_code=303)


@app.get("/appointments/{appointment_id}", response_class=HTMLResponse)
def appointment_detail(appointment_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)):
    appointment = (db.query(Appointment).options(joinedload(Appointment.patient), joinedload(Appointment.doctor),
                                                 joinedload(Appointment.consultation).joinedload(Consultation.prescriptions))
                   .filter(Appointment.id == appointment_id).first())
    if not appointment: raise HTTPException(404)
    invoice = db.query(Invoice).filter_by(appointment_id=appointment_id).first()
    return page(request, "appointment_detail.html", user, appointment=appointment, invoice=invoice)


@app.post("/appointments/{appointment_id}/status")
def set_status(appointment_id: int, request: Request, appointment_status: Annotated[AppointmentStatus, Form()],
               db: Session = Depends(get_db), user: User = Depends(current_user)):
    appointment = db.get(Appointment, appointment_id)
    if not appointment: raise HTTPException(404)
    appointment.status = appointment_status
    audit(db, user.id, "status_change", "appointment", str(appointment_id), appointment_status.value,
          request.client.host if request.client else None); db.commit()
    return RedirectResponse(f"/appointments/{appointment_id}", status_code=303)


@app.post("/appointments/{appointment_id}/consultation")
def save_consultation(appointment_id: int, request: Request, symptoms: Annotated[str, Form()] = "",
                      vitals: Annotated[str, Form()] = "", examination: Annotated[str, Form()] = "",
                      diagnosis: Annotated[str, Form()] = "", care_plan: Annotated[str, Form()] = "",
                      follow_up_date: Annotated[str, Form()] = "", doctor_confirmed: Annotated[str | None, Form()] = None,
                      db: Session = Depends(get_db), user: User = Depends(current_user)):
    appointment = db.query(Appointment).options(joinedload(Appointment.patient), joinedload(Appointment.consultation)).get(appointment_id)
    if not appointment: raise HTTPException(404)
    consultation = appointment.consultation or Consultation(appointment_id=appointment_id)
    consultation.symptoms, consultation.vitals, consultation.examination = symptoms, vitals, examination
    consultation.diagnosis, consultation.care_plan = diagnosis, care_plan
    consultation.follow_up_date = date.fromisoformat(follow_up_date) if follow_up_date else None
    consultation.ai_summary = clinical_support(appointment.patient, symptoms, vitals)
    consultation.doctor_confirmed = doctor_confirmed == "on"
    db.add(consultation)
    if consultation.doctor_confirmed: appointment.status = AppointmentStatus.COMPLETED
    audit(db, user.id, "save", "consultation", str(consultation.id or "new"), "Clinical note updated",
          request.client.host if request.client else None); db.commit()
    return RedirectResponse(f"/appointments/{appointment_id}", status_code=303)


@app.post("/appointments/{appointment_id}/prescriptions")
def add_prescription(appointment_id: int, medicine: Annotated[str, Form()], dosage: Annotated[str, Form()],
                     frequency: Annotated[str, Form()], duration: Annotated[str, Form()], instructions: Annotated[str, Form()] = "",
                     db: Session = Depends(get_db), user: User = Depends(current_user)):
    appointment = db.query(Appointment).options(joinedload(Appointment.consultation)).get(appointment_id)
    if not appointment: raise HTTPException(404)
    if not appointment.consultation:
        appointment.consultation = Consultation(appointment_id=appointment_id)
        db.flush()
    db.add(Prescription(consultation_id=appointment.consultation.id, medicine=medicine, dosage=dosage,
                        frequency=frequency, duration=duration, instructions=instructions or None))
    audit(db, user.id, "create", "prescription", detail=f"Prescription added to appointment {appointment_id}"); db.commit()
    return RedirectResponse(f"/appointments/{appointment_id}", status_code=303)


@app.post("/appointments/{appointment_id}/invoice")
def save_invoice(appointment_id: int, amount: Annotated[float, Form()], payment_status: Annotated[str, Form()],
                 payment_method: Annotated[str, Form()] = "", db: Session = Depends(get_db), user: User = Depends(current_user)):
    invoice = db.query(Invoice).filter_by(appointment_id=appointment_id).first() or Invoice(appointment_id=appointment_id, amount=amount)
    invoice.amount, invoice.payment_status, invoice.payment_method = amount, payment_status, payment_method or None
    db.add(invoice); audit(db, user.id, "save", "invoice", str(invoice.id or "new"), f"Status: {payment_status}"); db.commit()
    return RedirectResponse(f"/appointments/{appointment_id}", status_code=303)


@app.get("/reminders", response_class=HTMLResponse)
def reminders(request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)):
    upcoming = (db.query(Appointment).options(joinedload(Appointment.patient), joinedload(Appointment.doctor))
                .filter(Appointment.scheduled_at >= datetime.now(), Appointment.status == AppointmentStatus.BOOKED)
                .order_by(Appointment.scheduled_at).limit(100).all())
    return page(request, "reminders.html", user, appointments=upcoming)


@app.post("/reminders/{appointment_id}/send")
def send_reminder(appointment_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    appointment = db.get(Appointment, appointment_id)
    if not appointment: raise HTTPException(404)
    appointment.reminder_sent = True
    audit(db, user.id, "send", "reminder", str(appointment_id), "Demo reminder marked sent"); db.commit()
    return RedirectResponse("/reminders", status_code=303)


@app.get("/reports", response_class=HTMLResponse)
def reports(request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)):
    status_rows = db.query(Appointment.status, func.count(Appointment.id)).group_by(Appointment.status).all()
    revenue = db.query(func.coalesce(func.sum(Invoice.amount), 0)).filter(Invoice.payment_status == "paid").scalar()
    return page(request, "reports.html", user, status_rows=status_rows, revenue=revenue)


@app.get("/users", response_class=HTMLResponse)
def users(request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if user.role != Role.ADMIN: raise HTTPException(403)
    return page(request, "users.html", user, users=db.query(User).order_by(User.full_name).all())


@app.post("/users")
def create_user(full_name: Annotated[str, Form()], email: Annotated[str, Form()], password: Annotated[str, Form()],
                role: Annotated[Role, Form()], db: Session = Depends(get_db), user: User = Depends(current_user)):
    if user.role != Role.ADMIN: raise HTTPException(403)
    if db.query(User).filter(func.lower(User.email) == email.lower()).first(): raise HTTPException(400, "Email already exists")
    db.add(User(full_name=full_name, email=email.lower(), password_hash=hash_password(password), role=role))
    audit(db, user.id, "create", "user", detail=f"Created {role.value} account"); db.commit()
    return RedirectResponse("/users", status_code=303)

