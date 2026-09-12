# MediCare Clinic Intelligence

A GitHub-ready clinic analytics dashboard for managing patients, appointments, doctors, billing, and operational KPIs.

> **Important:** This project uses demo/fake data. It is not a medical device and must not be used with real patient data without a proper security, privacy, compliance, and clinical review.

## Stack

- Frontend: React + Vite
- Backend: Node.js + Express
- Database: PostgreSQL
- Charts: Recharts
- Authentication: JWT
- Styling: CSS

## Features

- Dashboard with clinic KPIs
- Patient management
- Doctor directory
- Appointment management
- Billing records
- Revenue and appointment analytics
- PostgreSQL schema + seed data
- JWT login
- REST API
- Responsive UI

## Project structure

```text
MediCare-Clinic-Intelligence/
├── client/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   └── package.json
├── server/
│   ├── src/
│   │   ├── middleware/auth.js
│   │   ├── routes/
│   │   ├── db.js
│   │   └── index.js
│   ├── .env.example
│   └── package.json
├── database/
│   ├── schema.sql
│   └── seed.sql
└── README.md
```

## Run locally

### 1. Create PostgreSQL database

```sql
CREATE DATABASE medicare_clinic;
```

Run:

```bash
psql -U postgres -d medicare_clinic -f database/schema.sql
psql -U postgres -d medicare_clinic -f database/seed.sql
```

### 2. Start API

```bash
cd server
npm install
cp .env.example .env
npm run dev
```

### 3. Start frontend

Open another terminal:

```bash
cd client
npm install
npm run dev
```

Frontend: http://localhost:5173  
API: http://localhost:5000

### Demo login

```text
Email: admin@medicare.local
Password: Admin@123
```

Change this password before using the application anywhere beyond a local demo.

## Environment

Server `.env`:

```env
PORT=5000
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/medicare_clinic
JWT_SECRET=replace-with-a-long-random-secret
CLIENT_URL=http://localhost:5173
```

## GitHub

```bash
git init
git add .
git commit -m "Initial MediCare Clinic Intelligence project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/medicare-clinic-intelligence.git
git push -u origin main
```

Never commit `.env`, passwords, API keys, database credentials, or real patient information.
