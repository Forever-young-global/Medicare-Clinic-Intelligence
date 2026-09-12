-- Demo password hash for Admin@123.
-- Generated with bcryptjs-compatible bcrypt hash.
INSERT INTO users (name, email, password_hash, role)
VALUES ('Clinic Administrator', 'admin@medicare.local',
        '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy',
        'admin');

INSERT INTO doctors (name, specialty, phone, email) VALUES
('Dr. Ananya Rao', 'General Medicine', '+91 90000 10001', 'ananya@medicare.local'),
('Dr. Arjun Menon', 'Cardiology', '+91 90000 10002', 'arjun@medicare.local'),
('Dr. Meera Nair', 'Dermatology', '+91 90000 10003', 'meera@medicare.local'),
('Dr. Rahul Shah', 'Orthopedics', '+91 90000 10004', 'rahul@medicare.local');

INSERT INTO patients
(patient_code, name, date_of_birth, gender, phone, email, address, blood_group)
VALUES
('P-1001','Aarav Kumar','1994-04-12','Male','9000010001','aarav@example.com','Bengaluru','O+'),
('P-1002','Diya Sharma','1988-09-21','Female','9000010002','diya@example.com','Mysuru','A+'),
('P-1003','Rohan Thomas','1979-01-07','Male','9000010003','rohan@example.com','Mangaluru','B+'),
('P-1004','Nisha Joseph','1997-11-15','Female','9000010004','nisha@example.com','Bengaluru','AB+'),
('P-1005','Kabir Singh','1968-06-03','Male','9000010005','kabir@example.com','Tumakuru','O-'),
('P-1006','Sara Fernandes','2001-03-29','Female','9000010006','sara@example.com','Udupi','A-');

INSERT INTO appointments
(patient_id, doctor_id, appointment_date, reason, status)
VALUES
(1,1,NOW() + INTERVAL '1 hour','Routine consultation','Scheduled'),
(2,2,NOW() + INTERVAL '3 hours','Follow-up','Scheduled'),
(3,4,NOW() + INTERVAL '1 day','Knee pain','Scheduled'),
(4,3,NOW() + INTERVAL '2 days','Skin consultation','Scheduled'),
(5,2,NOW() - INTERVAL '1 day','Cardiology review','Completed'),
(6,1,NOW() - INTERVAL '2 days','Fever','Completed');

INSERT INTO invoices
(patient_id, invoice_number, amount, payment_status, issued_at, paid_at)
VALUES
(1,'INV-10001',1200,'Paid',NOW()-INTERVAL '3 days',NOW()-INTERVAL '3 days'),
(2,'INV-10002',2500,'Paid',NOW()-INTERVAL '2 days',NOW()-INTERVAL '1 day'),
(3,'INV-10003',1800,'Pending',NOW()-INTERVAL '1 day',NULL),
(4,'INV-10004',900,'Paid',NOW()-INTERVAL '4 days',NOW()-INTERVAL '4 days'),
(5,'INV-10005',3200,'Pending',NOW(),NULL);
