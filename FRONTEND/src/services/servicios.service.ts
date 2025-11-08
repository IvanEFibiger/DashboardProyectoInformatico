// src/services/servicios.service.ts
import { api } from '../api/axios'

export interface Servicio {
  id: number
  nombre: string
  descripcion: string
  precio: number
  id_usuario?: number
  activo?: number
}

export interface PagedServiciosResponse {
  total_pages: number
  current_page: number
  service: Servicio[]            
}

const normalize = (raw: any): Servicio => ({
  id: Number(raw.id ?? raw.servicio_id),
  nombre: raw.nombre ?? '',
  descripcion: raw.descripcion ?? '',
  precio: Number(raw.precio ?? 0),
  id_usuario: raw.id_usuario,
  activo: raw.activo,
})

export const ServiciosService = {
  getPaged: async (userId: string | number, page = 1): Promise<PagedServiciosResponse> => {
    const { data } = await api.get(`/usuarios/${userId}/servicios-paginados`, { params: { page } })
    return {
      total_pages: data.total_pages ?? 1,
      current_page: data.current_page ?? page,
      service: Array.isArray(data.service) ? data.service.map(normalize) : [], 
    }
  },

  getById: async (userId: string | number, id: number): Promise<Servicio> => {
    const { data } = await api.get(`/usuarios/${userId}/servicios/${id}`)
    return normalize(data)
  },

  create: async (
    userId: string | number,
    body: { nombre: string; precio: number; descripcion?: string }
  ): Promise<Servicio> => {
    const { data } = await api.post(`/usuarios/${userId}/servicios`, body)
    return normalize(data)
  },

  update: async (
    userId: string | number,
    id: number,
    body: { nombre: string; precio: number; descripcion?: string }
  ): Promise<Servicio> => {
    const { data } = await api.put(`/usuarios/${userId}/servicios/${id}`, body)
    return normalize(data)
  },

  remove: async (userId: string | number, id: number): Promise<{ message: string; id: number }> => {
    const { data } = await api.delete(`/usuarios/${userId}/servicios/${id}`)
    return data
  },
}
