const BASE = import.meta.env.VITE_API_URL ?? '/api'

function getToken() {
  return localStorage.getItem('token')
}

export function setToken(token: string) {
  localStorage.setItem('token', token)
}

export function clearToken() {
  localStorage.removeItem('token')
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${path}`, { ...options, headers })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Something went wrong')
  }
  return res.json()
}

export const api = {
  sendOtp: (phone: string) =>
    request('/auth/send-otp', { method: 'POST', body: JSON.stringify({ phone }) }),

  verifyOtp: (phone: string, code: string) =>
    request<{ access_token: string }>('/auth/verify-otp', {
      method: 'POST',
      body: JSON.stringify({ phone, code }),
    }),

  getVenues: () =>
    request<{ key: string; name: string }[]>('/venues'),

  getPreferences: () =>
    request<{ venue_keys: string[] }>('/preferences'),

  updatePreferences: (venue_keys: string[]) =>
    request('/preferences', { method: 'PUT', body: JSON.stringify({ venue_keys }) }),

  getAdminStats: () => request('/admin/stats'),
  getAdminUsers: () => request('/admin/users'),
  getAdminGames: () => request('/admin/games'),
}
