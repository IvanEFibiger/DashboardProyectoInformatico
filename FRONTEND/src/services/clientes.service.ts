// src/services/clientes.service.ts
import { api } from '../api/axios'

export interface Cliente {
  id: number
  nombre: string
  email: string
  direccion: string
  cuit: string
  id_usuario?: number
  activo?: number
}

export interface PagedClientesResponse {
  total_pages: number
  current_page: number
  clients: Cliente[]
}

const normalizeCliente = (raw: any): Cliente => ({
  id: raw.id ?? raw.cliente_id, 
  nombre: raw.nombre ?? '',
  email: raw.email ?? '',
  direccion: raw.direccion ?? '',
  cuit: raw.cuit ?? '',
  id_usuario: raw.id_usuario,
  activo: raw.activo,
})

export const ClientesService = {
  getPaged: async (userId: string | number, page = 1): Promise<PagedClientesResponse> => {
    const { data } = await api.get(`/usuarios/${userId}/clientes-paginados`, { params: { page } })
    return {
      total_pages: data.total_pages ?? 1,
      current_page: data.current_page ?? page,
      clients: Array.isArray(data.clients) ? data.clients.map(normalizeCliente) : [],
    }
  },

  getById: async (userId: string | number, id: number): Promise<Cliente> => {
    const { data } = await api.get(`/usuarios/${userId}/clientes/${id}`)
    return normalizeCliente(data)
  },

  create: async (userId: string | number, body: Partial<Cliente>): Promise<Cliente> => {
    const { data } = await api.post(`/usuarios/${userId}/clientes`, body)
    return normalizeCliente(data)
  },

  update: async (userId: string | number, id: number, body: Partial<Cliente>): Promise<Cliente> => {
    const { data } = await api.put(`/usuarios/${userId}/clientes/${id}`, body)
    return normalizeCliente(data)
  },

  remove: async (userId: string | number, id: number): Promise<{ message: string; id: number }> => {
    const { data } = await api.delete(`/usuarios/${userId}/clientes/${id}`)
    return data
  },
}
