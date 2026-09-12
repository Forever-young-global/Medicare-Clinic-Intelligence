import { useEffect, useState } from 'react';
import {
  Activity, CalendarDays, CircleDollarSign, LogOut, Menu,
  Users, UserRound, Receipt, LayoutDashboard, Search, Plus
} from 'lucide-react';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  Tooltip, CartesianGrid, BarChart, Bar
} from 'recharts';
import { api } from './api';

const nav = [
  ['dashboard', 'Dashboard', LayoutDashboard],
  ['patients', 'Patients', Users],
  ['doctors', 'Doctors', UserRound],
  ['appointments', 'Appointments', CalendarDays],
  ['billing', 'Billing', Receipt]
];

function Login({ onLogin }) {
  const [email, setEmail] = useState('admin@medicare.local');
  const [password, setPassword] = useState('Admin@123');
  const [error, setError] = useState('');

  async function submit(e) {
    e.preventDefault();
    setError('');
    try {
      const data = await api.login({ email, password });
      localStorage.setItem('medicare_token', data.token);
      onLogin(data.user);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="brand-mark"><Activity size={26}/></div>
        <h1>MediCare</h1>
        <p>Clinic Intelligence</p>
        <form onSubmit={submit}>
          <label>Email</label>
          <input value={email} onChange={e => setEmail(e.target.value)} />
          <label>Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} />
          {error && <div className="error">{error}</div>}
          <button className="primary full">Sign in</button>
        </form>
        <small>Demo account is prefilled.</small>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, detail }) {
  return (
    <div className="stat-card">
      <div className="stat-icon"><Icon size={21}/></div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        <small>{detail}</small>
      </div>
    </div>
  );
}

function Dashboard({ data }) {
  const k = data?.kpis || {};
  return (
    <>
      <div className="page-heading">
        <div><h2>Clinic overview</h2><p>Operational performance at a glance.</p></div>
      </div>
      <div className="stats">
        <StatCard icon={Users} label="Active patients" value={k.patients ?? '-'} detail="Registered patients" />
        <StatCard icon={CalendarDays} label="Today's appointments" value={k.todayAppointments ?? '-'} detail="Scheduled for today" />
        <StatCard icon={CircleDollarSign} label="Collected revenue" value={`₹${(k.revenue || 0).toLocaleString('en-IN')}`} detail="Paid invoices" />
        <StatCard icon={Receipt} label="Outstanding" value={`₹${(k.pending || 0).toLocaleString('en-IN')}`} detail="Pending invoices" />
      </div>
      <div className="chart-grid">
        <section className="panel">
          <div className="panel-title"><h3>Revenue trend</h3><span>Paid invoices</span></div>
          <div className="chart">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data?.monthlyRevenue || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(v) => [`₹${Number(v).toLocaleString('en-IN')}`, 'Revenue']} />
                <Line type="monotone" dataKey="revenue" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>
        <section className="panel">
          <div className="panel-title"><h3>Appointment status</h3><span>All appointments</span></div>
          <div className="chart">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.appointmentStatus || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="status" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>
    </>
  );
}

function Table({ columns, rows }) {
  return (
    <div className="table-wrap">
      <table>
        <thead><tr>{columns.map(c => <th key={c.key}>{c.label}</th>)}</tr></thead>
        <tbody>
          {rows.length ? rows.map(row => (
            <tr key={row.id}>{columns.map(c => <td key={c.key}>{c.render ? c.render(row) : row[c.key]}</td>)}</tr>
          )) : <tr><td colSpan={columns.length} className="empty">No records found.</td></tr>}
        </tbody>
      </table>
    </div>
  );
}

function Patients({ rows, reload }) {
  const [search, setSearch] = useState('');
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ patient_code:'', name:'', gender:'', phone:'', email:'', blood_group:'' });

  async function submit(e) {
    e.preventDefault();
    await api.createPatient(form);
    setForm({ patient_code:'', name:'', gender:'', phone:'', email:'', blood_group:'' });
    setOpen(false);
    reload();
  }

  return (
    <>
      <div className="page-heading">
        <div><h2>Patients</h2><p>Search and manage patient records.</p></div>
        <button className="primary" onClick={() => setOpen(true)}><Plus size={18}/> Add patient</button>
      </div>
      <div className="toolbar">
        <Search size={18}/>
        <input placeholder="Search name, patient code or phone" value={search}
          onChange={e => setSearch(e.target.value)} onKeyDown={e => e.key === 'Enter' && reload(search)} />
        <button className="secondary" onClick={() => reload(search)}>Search</button>
      </div>
      <section className="panel">
        <Table rows={rows} columns={[
          {key:'patient_code', label:'Patient ID'},
          {key:'name', label:'Name'},
          {key:'gender', label:'Gender'},
          {key:'phone', label:'Phone'},
          {key:'blood_group', label:'Blood group'},
          {key:'status', label:'Status', render:r=><span className="badge">{r.status}</span>}
        ]}/>
      </section>
      {open && <div className="modal-backdrop"><form className="modal" onSubmit={submit}>
        <h3>Add patient</h3>
        {['patient_code','name','gender','phone','email','blood_group'].map(key =>
          <input key={key} required={key==='patient_code'||key==='name'} placeholder={key.replace('_',' ')}
            value={form[key]} onChange={e=>setForm({...form,[key]:e.target.value})}/>
        )}
        <div className="modal-actions">
          <button type="button" className="secondary" onClick={()=>setOpen(false)}>Cancel</button>
          <button className="primary">Save patient</button>
        </div>
      </form></div>}
    </>
  );
}

function Doctors({ rows }) {
  return <>
    <div className="page-heading"><div><h2>Doctors</h2><p>Clinical team directory.</p></div></div>
    <section className="doctor-grid">
      {rows.map(d => <div className="doctor-card" key={d.id}>
        <div className="avatar">{d.name.split(' ').slice(1,2)[0]?.[0] || 'D'}</div>
        <h3>{d.name}</h3><p>{d.specialty}</p><small>{d.phone}</small><small>{d.email}</small>
        <span className="badge">{d.status}</span>
      </div>)}
    </section>
  </>;
}

function Appointments({ rows }) {
  return <>
    <div className="page-heading"><div><h2>Appointments</h2><p>Upcoming and completed visits.</p></div></div>
    <section className="panel"><Table rows={rows} columns={[
      {key:'appointment_date', label:'Date', render:r=>new Date(r.appointment_date).toLocaleString()},
      {key:'patient_name', label:'Patient'},
      {key:'doctor_name', label:'Doctor'},
      {key:'specialty', label:'Specialty'},
      {key:'reason', label:'Reason'},
      {key:'status', label:'Status', render:r=><span className="badge">{r.status}</span>}
    ]}/></section>
  </>;
}

function Billing({ rows }) {
  return <>
    <div className="page-heading"><div><h2>Billing</h2><p>Invoice and payment overview.</p></div></div>
    <section className="panel"><Table rows={rows} columns={[
      {key:'invoice_number', label:'Invoice'},
      {key:'patient_name', label:'Patient'},
      {key:'amount', label:'Amount', render:r=>`₹${Number(r.amount).toLocaleString('en-IN')}`},
      {key:'issued_at', label:'Issued', render:r=>new Date(r.issued_at).toLocaleDateString()},
      {key:'payment_status', label:'Payment', render:r=><span className="badge">{r.payment_status}</span>}
    ]}/></section>
  </>;
}

export default function App() {
  const [user, setUser] = useState(null);
  const [page, setPage] = useState('dashboard');
  const [data, setData] = useState(null);
  const [patients, setPatients] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(false);

  async function loadAll(search='') {
    setLoading(true);
    try {
      const [dash, p, d, a, i] = await Promise.all([
        api.dashboard(), api.patients(search), api.doctors(), api.appointments(), api.invoices()
      ]);
      setData(dash); setPatients(p); setDoctors(d); setAppointments(a); setInvoices(i);
    } finally { setLoading(false); }
  }

  useEffect(() => {
    if (localStorage.getItem('medicare_token')) {
      const saved = localStorage.getItem('medicare_user');
      setUser(saved ? JSON.parse(saved) : { name: 'Administrator', role: 'admin' });
    }
  }, []);

  useEffect(() => { if (user) loadAll(); }, [user]);

  function login(u) {
    localStorage.setItem('medicare_user', JSON.stringify(u));
    setUser(u);
  }

  if (!user) return <Login onLogin={login}/>;

  const current = {
    dashboard: <Dashboard data={data}/>,
    patients: <Patients rows={patients} reload={loadAll}/>,
    doctors: <Doctors rows={doctors}/>,
    appointments: <Appointments rows={appointments}/>,
    billing: <Billing rows={invoices}/>
  }[page];

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="logo"><div className="brand-mark"><Activity size={21}/></div><div><b>MediCare</b><small>Clinic Intelligence</small></div></div>
      <nav>{nav.map(([key,label,Icon]) =>
        <button key={key} className={page===key?'active':''} onClick={()=>setPage(key)}><Icon size={19}/>{label}</button>
      )}</nav>
      <div className="side-bottom">
        <div className="user-mini"><div className="avatar">A</div><div><b>{user.name}</b><small>{user.role}</small></div></div>
        <button onClick={()=>{localStorage.clear();setUser(null)}}><LogOut size={18}/> Sign out</button>
      </div>
    </aside>
    <main className="main">
      <header><button className="mobile-menu"><Menu/></button><div className="status"><span></span> System operational</div><span>{loading?'Refreshing…':''}</span></header>
      <div className="content">{current}</div>
    </main>
  </div>;
}
