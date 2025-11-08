// src/security/localAuth.ts
export function getToken(): string | null { return localStorage.getItem('token') }
export function getUserId(): string | null { return localStorage.getItem('userId') }
export function getUsername(): string | null {
  const user = localStorage.getItem('user')
  try { return user ? (JSON.parse(user)?.username || JSON.parse(user)?.nombre) : null } catch { return null }
}
export function setAuth({ token, id, user }: { token: string; id: string; user?: any }) {
  localStorage.setItem('token', token)
  localStorage.setItem('userId', id)
  if (user) localStorage.setItem('user', JSON.stringify(user))
}
export function clearAuth() {
  localStorage.removeItem('token')
  localStorage.removeItem('userId')
  localStorage.removeItem('user')
}


export function setToken(token: string) {
  localStorage.setItem('token', token)
}
