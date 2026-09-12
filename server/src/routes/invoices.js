import { Router } from 'express';
import { query } from '../db.js';

const router = Router();

router.get('/', async (_req, res) => {
  const result = await query(`
    SELECT i.*, p.patient_code, p.name AS patient_name
    FROM invoices i
    JOIN patients p ON p.id = i.patient_id
    ORDER BY i.issued_at DESC
  `);
  res.json(result.rows);
});

export default router;
