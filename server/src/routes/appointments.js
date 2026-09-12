import { Router } from 'express';
import { query } from '../db.js';

const router = Router();

router.get('/', async (_req, res) => {
  const result = await query(`
    SELECT a.id, a.appointment_date, a.reason, a.status,
           p.patient_code, p.name AS patient_name,
           d.name AS doctor_name, d.specialty
    FROM appointments a
    JOIN patients p ON p.id = a.patient_id
    JOIN doctors d ON d.id = a.doctor_id
    ORDER BY a.appointment_date DESC
  `);
  res.json(result.rows);
});

router.post('/', async (req, res) => {
  const { patient_id, doctor_id, appointment_date, reason } = req.body;

  if (!patient_id || !doctor_id || !appointment_date) {
    return res.status(400).json({ message: 'Patient, doctor and date are required' });
  }

  const result = await query(
    `INSERT INTO appointments
     (patient_id, doctor_id, appointment_date, reason)
     VALUES ($1,$2,$3,$4) RETURNING *`,
    [patient_id, doctor_id, appointment_date, reason || null]
  );

  res.status(201).json(result.rows[0]);
});

router.patch('/:id/status', async (req, res) => {
  const result = await query(
    'UPDATE appointments SET status=$1 WHERE id=$2 RETURNING *',
    [req.body.status, req.params.id]
  );
  res.json(result.rows[0]);
});

export default router;
