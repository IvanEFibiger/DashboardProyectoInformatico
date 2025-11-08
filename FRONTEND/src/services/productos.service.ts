// src/services/productos.service.ts
import { api } from '../api/axios'

export interface Producto {
  id: number
  nombre: string
  descripcion: string
  precio: number
  cantidad: number 
  id_usuario?: number
  activo?: number
}

export interface PagedProductosResponse {
  total_pages: number
  current_page: number
  products: Producto[]
}

const normalize = (raw: any): Producto => ({
  id: Number(raw.id ?? raw.producto_id),
  nombre: raw.nombre ?? '',
  descripcion: raw.descripcion ?? '',
  precio: Number(raw.precio ?? 0),
  cantidad: Number(raw.cantidad ?? raw.stock_actual ?? 0),
  id_usuario: raw.id_usuario,
  activo: raw.activo,
})

export const ProductosService = {
  getPaged: async (userId: string | number, page = 1): Promise<PagedProductosResponse> => {
    const { data } = await api.get(`/usuarios/${userId}/productos-paginados`, { params: { page } })
    return {
      total_pages: data.total_pages ?? 1,
      current_page: data.current_page ?? page,
      products: Array.isArray(data.products) ? data.products.map(normalize) : [],
    }
  },

  getById: async (userId: string | number, id: number): Promise<Producto> => {
    const { data } = await api.get(`/usuarios/${userId}/productos/${id}`)
    return normalize(data)
  },

  create: async (
    userId: string | number,
    body: { nombre: string; precio: number; cantidad: number; descripcion?: string }
  ): Promise<Producto> => {
    const { data } = await api.post(`/usuarios/${userId}/productos`, body)
    return normalize(data)
  },

  update: async (
    userId: string | number,
    id: number,
    body: { nombre: string; precio: number; descripcion?: string }
  ): Promise<Producto> => {
    const { data } = await api.put(`/usuarios/${userId}/productos/${id}`, body)
    return normalize(data)
  },

  remove: async (userId: string | number, id: number): Promise<{ message: string; id: number }> => {
    const { data } = await api.delete(`/usuarios/${userId}/productos/${id}`)
    return data
  },

  cargarStock: async (
    userId: string | number,
    id: number,
    cantidad: number
  ): Promise<{ message: string; stock_real: number }> => {
    const { data } = await api.put(`/usuarios/${userId}/productos/${id}/stock`, { cantidad })
    return data
  },
}
