import { Router } from 'express';
import { query } from '../db.js';

const router = Router();

router.get('/', async (_req, res) => {
  const result = await query('SELECT * FROM doctors ORDER BY name');
  res.json(result.rows);
});

export default router;
