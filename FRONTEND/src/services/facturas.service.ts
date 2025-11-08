import { api } from '../api/axios'

export interface FacturaDetalleItemList {
  factura_id: number
  fecha_emision: string
  nombre_cliente: string
  total: number
}

export interface FacturasPagedResponse {
  total_pages: number
  current_page: number
  facturas_detalles: FacturaDetalleItemList[]
}

export interface DetalleFactura {
  id: number
  id_factura: number
  id_producto: number | null
  id_servicio: number | null
  cantidad: number
  precio_unitario: number
  subtotal: number
}

export interface FacturaFullResponse {
  factura: {
    id: number
    fecha_emision: string
    id_clientes: number
    id_usuario: number
    total: number
  }
  cliente: {
    nombre_cliente: string
    cuit_cliente: string
  }
  detalles: DetalleFactura[]
  productos_servicios: Array<{
    id: number
    nombre: string
    descripcion?: string
    precio?: number
  }>
  total: number
}

export const FacturasService = {
  getPaged: (userId: string | number, page = 1): Promise<FacturasPagedResponse> =>
    api
      .get(`/usuarios/${userId}/facturas/detalles`, { params: { page } })
      .then(r => r.data),

  getDetalle: (userId: string | number, id: number): Promise<FacturaFullResponse> =>
    api.get(`/usuarios/${userId}/factura/${id}`).then(r => r.data),

  create: (userId: string | number, body: any): Promise<{ factura_id: number; total: number }> =>
    api.post(`/usuarios/${userId}/factura`, body).then(r => r.data),

  remove: (userId: string | number, id: number): Promise<{ message: string; factura_id: number }> =>
    api.delete(`/usuarios/${userId}/factura/${id}`).then(r => r.data),
}
