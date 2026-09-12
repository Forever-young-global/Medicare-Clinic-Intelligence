import { Router } from 'express';
import { query } from '../db.js';

const router = Router();

router.get('/', async (req, res) => {
  const search = req.query.search || '';
  const result = await query(
    `SELECT * FROM patients
     WHERE name ILIKE $1 OR patient_code ILIKE $1 OR phone ILIKE $1
     ORDER BY created_at DESC`,
    [`%${search}%`]
  );
  res.json(result.rows);
});

router.post('/', async (req, res) => {
  const {
    patient_code, name, date_of_birth, gender, phone, email, address, blood_group
  } = req.body;

  if (!patient_code || !name) {
    return res.status(400).json({ message: 'Patient code and name are required' });
  }

  const result = await query(
    `INSERT INTO patients
     (patient_code,name,date_of_birth,gender,phone,email,address,blood_group)
     VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
     RETURNING *`,
    [patient_code, name, date_of_birth || null, gender || null, phone || null,
     email || null, address || null, blood_group || null]
  );

  res.status(201).json(result.rows[0]);
});

export default router;
