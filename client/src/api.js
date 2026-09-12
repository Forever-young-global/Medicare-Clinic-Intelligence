const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

async function request(path, options = {}) {
  const token = localStorage.getItem('medicare_token');

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {})
    }
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.message || 'Request failed');
  }

  return data;
}

export const api = {
  login: (body) => request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(body)
  }),
  dashboard: () => request('/dashboard'),
  patients: (search = '') => request(`/patients?search=${encodeURIComponent(search)}`),
  doctors: () => request('/doctors'),
  appointments: () => request('/appointments'),
  invoices: () => request('/invoices'),
  createPatient: (body) => request('/patients', {
    method: 'POST',
    body: JSON.stringify(body)
  })
};
