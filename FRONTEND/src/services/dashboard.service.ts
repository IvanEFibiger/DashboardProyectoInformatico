// src/services/dashboard.service.ts
import { api } from '../api/axios'

type StockProd = { id: number; nombre: string; cantidad: number }


export type RangeKey = 'mes' | 'trim' | 'anio' | 'todo'

export type MovimientoReciente = {
  fecha: string
  factura_id: number
  tipo: 'producto' | 'servicio'
  item_id: number
  item_nombre: string
  cantidad: number
  precio_unitario: number
  subtotal: number
  cliente: string
}

function fmtLocalYMD(d: Date) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${dd}`
}

export function makeRangeQuery(range: RangeKey): string {
  if (range === 'todo') return ''
  const now = new Date()
  
  const to = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  let from = new Date(to) 

  if (range === 'mes') {
    from = new Date(to.getFullYear(), to.getMonth(), 1)
  } else if (range === 'trim') {
    
    from = new Date(to.getFullYear(), to.getMonth() - 2, 1)
  } else if (range === 'anio') {
    from = new Date(to.getFullYear(), 0, 1)
  }

  const qs = `from=${fmtLocalYMD(from)}&to=${fmtLocalYMD(to)}`
  return qs
}

function withQuery(path: string, qs: string) {
  if (!qs) return path
  return path.includes('?') ? `${path}&${qs}` : `${path}?${qs}`
}

async function safeGet<T>(path: string, fallback: T): Promise<T> {
  try {
    const r = await api.get<T>(path)
    return r.data
  } catch {
    return fallback
  }
}

export const DashboardService = {
  ingresosTotales: (userId: string, range: RangeKey = 'todo') =>
    safeGet<{ total_facturas_usuario: number }>(
      withQuery(`/usuarios/${userId}/factura/total`, makeRangeQuery(range)),
      { total_facturas_usuario: 0 }
    ),

  cantidadFacturas: (userId: string, range: RangeKey = 'todo') =>
    safeGet<{ cantidad_facturas_usuario: number }>(
      withQuery(`/usuarios/${userId}/factura/cantidad`, makeRangeQuery(range)),
      { cantidad_facturas_usuario: 0 }
    ),

  prodMasVendido: (userId: string, range: RangeKey = 'todo') =>
    safeGet<{ producto_mas_vendido: string; cantidad_vendida: number }>(
      withQuery(`/usuarios/${userId}/factura/producto-mas-vendido`, makeRangeQuery(range)),
      { producto_mas_vendido: '-', cantidad_vendida: 0 }
    ),

  cantidadClientes: (userId: string) =>
    safeGet<{ cantidad_clientes: number }>(
      `/usuarios/${userId}/cantidad-clientes`,
      { cantidad_clientes: 0 }
    ),

  rankingProductos: (userId: string, range: RangeKey = 'todo') =>
    safeGet<Array<{ nombre_producto: string; cantidad_vendida: number }>>(
      withQuery(`/usuarios/${userId}/ranking-productos`, makeRangeQuery(range)),
      []
    ),

  rankingServicios: (userId: string, range: RangeKey = 'todo') =>
    safeGet<Array<{ nombre_servicio: string; cantidad_vendida: number }>>(
      withQuery(`/usuarios/${userId}/ranking-servicios`, makeRangeQuery(range)),
      []
    ),

  rankingClientes: (userId: string, range: RangeKey = 'todo') =>
    safeGet<Array<{ nombre_cliente: string; total_gastado: number }>>(
      withQuery(`/usuarios/${userId}/ranking-clientes`, makeRangeQuery(range)),
      []
    ),

  productosConStock: (userId: string) =>
    safeGet<StockProd[]>(`/usuarios/${userId}/productos`, []),

  lowStock: async (userId: string, umbral = 5) => {
    const prods = await DashboardService.productosConStock(userId)
    const bajos = prods
      .filter(p => Number.isFinite(p.cantidad))
      .filter(p => p.cantidad <= umbral)
      .sort((a, b) => (a.cantidad - b.cantidad) || a.nombre.localeCompare(b.nombre))

    const outOfStock = bajos.filter(p => p.cantidad <= 0).length
    return { bajos, outOfStock }
  },

  
  movimientosRecientes: (
    userId: string,
    range: RangeKey = 'todo',
    limit = 10,
    offset = 0
  ) =>
    safeGet<MovimientoReciente[]>(
      withQuery(
        `/usuarios/${userId}/movimientos-recientes?limit=${limit}&offset=${offset}`,
        makeRangeQuery(range)
      ),
      []
    ),
}
