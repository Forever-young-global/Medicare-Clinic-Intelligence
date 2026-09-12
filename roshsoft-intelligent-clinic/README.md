# Roshsoft Intelligent Clinic

An end-to-end, open-source clinic-management MVP created by **Roshan Ernest Pinto — Roshsoft Technologies**, with Ms Vyalary Vaz and Ms Kavya M. Bhat.

The project includes a responsive browser GUI, Python/FastAPI backend, SQLAlchemy relational model, PostgreSQL production configuration, SQLite development fallback, login and roles, patients, appointments, consultation notes, transparent clinical safety prompts, prescriptions, billing, reminders, aggregate reports, and audit logging.

## Important medical and privacy notice

This is a demonstration/MVP, not certified medical-device software and not production-ready without a formal security, privacy, clinical-safety, legal, and infrastructure review. Its rules-based clinical support does **not diagnose** and must never replace a qualified doctor's judgment. Do not enter real patient information until the deployment has been reviewed for applicable Indian laws, consent requirements, retention policies, breach response, backups, encryption, access controls, and organizational procedures.

## Quick start — local SQLite

Requires Python 3.11 or newer.

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

First-run administrator:

- Email: `admin@roshsoft.local`
- Password: `ChangeMe123!`

Change the starter credentials and `SECRET_KEY` before any shared deployment.

Optional demo data:

```bash
python seed_demo.py
```

## PostgreSQL with Docker

```bash
cp .env.example .env
# Edit SECRET_KEY and database password in both .env and docker-compose.yml
docker compose up --build
```

The web application becomes available at `http://localhost:8000`; interactive API metadata is at `/api/docs`.

## Main workflow

1. Administrator signs in and creates doctor/receptionist accounts.
2. Reception records consent and registers the patient.
3. Staff books and checks in an appointment.
4. Doctor records symptoms, vitals, examination, diagnosis, and plan.
5. The rules-only support module surfaces configured red-flag phrases and medication/allergy reminders.
6. Doctor reviews and confirms the clinical record.
7. Prescription and invoice are recorded.
8. Follow-up appears in the patient history; upcoming reminders can be queued.
9. Aggregate status and paid-revenue reporting supports clinic operations.
10. Sensitive record views and changes are written to an audit log.

## Data model

- `users`: administrators, doctors, and receptionists
- `patients`: identity, contact, consent, allergies, conditions, and medicines
- `appointments`: doctor, patient, time, reason, status, and reminder state
- `consultations`: symptoms, vitals, examination, diagnosis, plan, follow-up, decision-support text, doctor confirmation
- `prescriptions`: medicine instructions linked to a consultation
- `invoices`: amount and payment state linked to an appointment
- `audit_logs`: actor, action, entity, timestamp, and network address

## Integrating real messaging

`POST /reminders/{appointment_id}/send` currently marks a reminder as sent without contacting a patient. Connect this service only to an approved SMS, WhatsApp, or email provider. Keep message content minimal, capture communication consent, protect provider credentials in a secret manager, record delivery results, and never place sensitive diagnoses in ordinary notifications.

## Security work required before production

- Put the application behind HTTPS and set `SESSION_HTTPS_ONLY=true`.
- Replace the starter admin password and use a long random `SECRET_KEY`.
- Add password reset, MFA, session revocation, login throttling, and account lockout.
- Enforce role permissions per action; the MVP has authenticated access and an admin-only user screen but requires a full authorization matrix.
- Add CSRF protection to state-changing forms.
- Encrypt database volumes and backups; use a managed key service where appropriate.
- Store secrets outside source control and rotate them.
- Use Alembic migrations rather than automatic table creation.
- Add immutable/forwarded audit storage and monitoring.
- Add secure document upload with malware scanning and strict file controls.
- Conduct threat modelling, dependency scanning, penetration testing, disaster-recovery testing, and code review.
- Define consent, retention, correction, export, deletion, emergency access, and breach processes with qualified legal/clinical advisors.

## Tests

```bash
pytest -q
```

## Project structure

```text
app/
  config.py       Environment configuration
  database.py     SQLAlchemy engine and sessions
  models.py       Relational database model
  security.py     Argon2 password hashing
  services.py     Audit and clinical-support services
  main.py         Web routes and business workflow
  templates/      Server-rendered responsive GUI
  static/         Visual design
tests/            Automated service tests
Dockerfile        Web container
docker-compose.yml PostgreSQL + web stack
```

## License

MIT. Free to use and modify. Clinical, privacy, and regulatory responsibility remains with the deploying organization.

