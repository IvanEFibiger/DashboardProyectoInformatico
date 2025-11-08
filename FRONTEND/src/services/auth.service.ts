// src/services/auth.ts
import { api } from '../api/axios'
import { setAuth } from '../security/localAuth'

export async function login(email: string, password: string) {
  const { data } = await api.post('/login', { email, password })

  setAuth({ token: data.token, id: String(data.id) })


  const userRes = await api.get(`/usuarios/${data.id}`)
  setAuth({ token: data.token, id: String(data.id), user: userRes.data?.user_data })
  return userRes.data?.user_data
}

export async function logout() {
  try { await api.post('/logout') } catch {}
}
