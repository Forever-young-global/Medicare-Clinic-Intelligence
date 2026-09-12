import { Router } from 'express';
import { query } from '../db.js';

const router = Router();

router.get('/', async (_req, res) => {
  const [patients, appointments, revenue, pending] = await Promise.all([
    query(`SELECT COUNT(*)::int AS value FROM patients WHERE status='Active'`),
    query(`SELECT COUNT(*)::int AS value FROM appointments
           WHERE appointment_date::date = CURRENT_DATE`),
    query(`SELECT COALESCE(SUM(amount),0)::numeric AS value FROM invoices
           WHERE payment_status='Paid'`),
    query(`SELECT COALESCE(SUM(amount),0)::numeric AS value FROM invoices
           WHERE payment_status='Pending'`)
  ]);

  const monthly = await query(`
    SELECT TO_CHAR(DATE_TRUNC('month', issued_at), 'Mon YYYY') AS month,
           COALESCE(SUM(amount),0)::numeric AS revenue
    FROM invoices
    WHERE payment_status='Paid'
    GROUP BY DATE_TRUNC('month', issued_at)
    ORDER BY DATE_TRUNC('month', issued_at)
  `);

  const appointmentStatus = await query(`
    SELECT status, COUNT(*)::int AS count
    FROM appointments
    GROUP BY status
    ORDER BY count DESC
  `);

  res.json({
    kpis: {
      patients: patients.rows[0].value,
      todayAppointments: appointments.rows[0].value,
      revenue: Number(revenue.rows[0].value),
      pending: Number(pending.rows[0].value)
    },
    monthlyRevenue: monthly.rows.map(x => ({ ...x, revenue: Number(x.revenue) })),
    appointmentStatus: appointmentStatus.rows
  });
});

export default router;
