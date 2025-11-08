// src/pages/productos/ProductosPage.tsx
import { useEffect, useMemo, useState } from 'react'
import { ProductosService, type Producto } from '../../services/productos.service'
import { getUserId } from '../../security/localAuth'

type FormMode = 'create' | 'edit' | 'stock'

type CreateForm = {
  nombre: string
  descripcion: string
  precio: string
  cantidad: string
}

type EditForm = {
  nombre: string
  descripcion: string
  precio: string
}

type StockForm = {
  cantidad: string
}

const emptyCreate: CreateForm = { nombre: '', descripcion: '', precio: '', cantidad: '' }
const emptyEdit: EditForm = { nombre: '', descripcion: '', precio: '' }
const emptyStock: StockForm = { cantidad: '' }

export function ProductosPage() {
  const userId = getUserId() as string
  const [page, setPage] = useState(1)
  const [rows, setRows] = useState<Producto[]>([])
  const [totalPages, setTotalPages] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [isOpen, setIsOpen] = useState(false)
  const [mode, setMode] = useState<FormMode>('create')
  const [selected, setSelected] = useState<Producto | null>(null)
  const [createForm, setCreateForm] = useState<CreateForm>(emptyCreate)
  const [editForm, setEditForm] = useState<EditForm>(emptyEdit)
  const [stockForm, setStockForm] = useState<StockForm>(emptyStock)
  const [submitting, setSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await ProductosService.getPaged(userId, page)
      setRows(data.products)
      setTotalPages(data.total_pages)
    } catch (e: any) {
      const apiMsg = e?.response?.data?.message
      setError(apiMsg || e?.message || 'Error al cargar productos')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    
  }, [userId, page])

  const openCreate = () => {
    setMode('create')
    setSelected(null)
    setCreateForm(emptyCreate)
    setFormError(null)
    setIsOpen(true)
  }
  const openEdit = (p: Producto) => {
    setMode('edit')
    setSelected(p)
    setEditForm({ nombre: p.nombre, descripcion: p.descripcion, precio: String(p.precio) })
    setFormError(null)
    setIsOpen(true)
  }
  const openStock = (p: Producto) => {
    setMode('stock')
    setSelected(p)
    setStockForm(emptyStock)
    setFormError(null)
    setIsOpen(true)
  }
  const closeModal = () => {
    if (!submitting) setIsOpen(false)
  }

  const validateCreate = (f: CreateForm): string | null => {
    if (!f.nombre.trim()) return 'El nombre es obligatorio.'
    if (f.nombre.length > 150) return 'El nombre es demasiado largo.'
    if (!f.precio.trim() || isNaN(Number(f.precio))) return 'Precio inválido.'
    if (!f.cantidad.trim() || isNaN(Number(f.cantidad))) return 'Cantidad inicial inválida.'
    return null
  }
  const validateEdit = (f: EditForm): string | null => {
    if (!f.nombre.trim()) return 'El nombre es obligatorio.'
    if (f.nombre.length > 150) return 'El nombre es demasiado largo.'
    if (!f.precio.trim() || isNaN(Number(f.precio))) return 'Precio inválido.'
    return null
  }
  const validateStock = (f: StockForm): string | null => {
    if (!f.cantidad.trim() || isNaN(Number(f.cantidad))) return 'Cantidad inválida.'
    if (Number(f.cantidad) === 0) return 'La cantidad no puede ser 0.'
    if (Number(f.cantidad) < 0) return 'Sólo se permiten entradas (cantidad positiva).'
    return null
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setSubmitting(true)
      setFormError(null)

      if (mode === 'create') {
        const msg = validateCreate(createForm)
        if (msg) throw new Error(msg)
        await ProductosService.create(userId, {
          nombre: createForm.nombre.trim(),
          descripcion: createForm.descripcion.trim(),
          precio: Number(createForm.precio),
          cantidad: Number(createForm.cantidad),
        })
        await fetchData()
        setIsOpen(false)
      }

      if (mode === 'edit' && selected) {
        const msg = validateEdit(editForm)
        if (msg) throw new Error(msg)
        await ProductosService.update(userId, selected.id, {
          nombre: editForm.nombre.trim(),
          descripcion: editForm.descripcion.trim(),
          precio: Number(editForm.precio),
        })
        await fetchData()
        setIsOpen(false)
      }

      if (mode === 'stock' && selected) {
        const msg = validateStock(stockForm)
        if (msg) throw new Error(msg)
        await ProductosService.cargarStock(userId, selected.id, Number(stockForm.cantidad))
        await fetchData()
        setIsOpen(false)
      }
    } catch (e: any) {
      const apiMsg = e?.response?.data?.message
      setFormError(apiMsg || e?.message || 'Error al guardar')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('¿Eliminar este producto?')) return
    try {
      await ProductosService.remove(userId, id)
      if (rows.length === 1 && page > 1) setPage(p => p - 1)
      else fetchData()
    } catch (e: any) {
      alert(e?.response?.data?.message ?? e?.message ?? 'Error al eliminar')
    }
  }

  const title = useMemo(() => {
    if (mode === 'create') return 'Nuevo producto'
    if (mode === 'edit') return 'Editar producto'
    return 'Cargar stock'
  }, [mode])

  return (
    <div className="grid gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Productos</h1>
        <button
          onClick={openCreate}
          className="px-3 py-2 rounded-lg bg-slate-900 text-white hover:bg-slate-800"
        >
          + Nuevo
        </button>
      </div>

      <div className="rounded-2xl bg-white shadow p-4">
        {loading && <div className="text-sm mb-2">Cargando...</div>}
        {error && <div className="text-sm text-red-600 mb-2">{error}</div>}

        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                {['ID','Nombre','Descripción','Precio','Stock','Acciones'].map(h=> (
                  <th key={h} className="py-2 pr-6">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((p)=> (
                <tr key={p.id} className="border-b last:border-b-0">
                  <td className="py-2 pr-6">{p.id}</td>
                  <td className="py-2 pr-6">{p.nombre}</td>
                  <td className="py-2 pr-6">{p.descripcion}</td>
                  <td className="py-2 pr-6">{p.precio.toFixed(2)}</td>
                  <td className="py-2 pr-6">{p.cantidad}</td>
                  <td className="py-2 pr-6 flex gap-2">
                    <button
                      className="px-2 py-1 rounded bg-slate-900 text-white"
                      onClick={() => openEdit(p)}
                    >
                      Editar
                    </button>
                    <button
                      className="px-2 py-1 rounded bg-emerald-600 text-white"
                      onClick={() => openStock(p)}
                    >
                      Stock
                    </button>
                    <button
                      className="px-2 py-1 rounded bg-red-600 text-white"
                      onClick={() => handleDelete(p.id)}
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))}

              {!loading && rows.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-sm text-slate-500">
                    No hay productos para mostrar.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="flex items-center gap-2 justify-center mt-3">
          <button
            disabled={page<=1}
            onClick={()=>setPage(p=>p-1)}
            className="px-3 py-1 rounded bg-white border disabled:opacity-50"
          >
            Anterior
          </button>
          <span className="text-sm">{page} / {totalPages}</span>
          <button
            disabled={page>=totalPages}
            onClick={()=>setPage(p=>p+1)}
            className="px-3 py-1 rounded bg-white border disabled:opacity-50"
          >
            Siguiente
          </button>
        </div>
      </div>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/40" onClick={closeModal} />
          <div className="relative z-10 w-full max-w-md rounded-2xl bg-white shadow p-5">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold">{title}</h3>
              <button onClick={closeModal} className="text-slate-500 hover:text-slate-700">✕</button>
            </div>

            {formError && (
              <div className="mb-3 rounded-md border border-red-200 bg-red-50 text-red-700 px-3 py-2 text-sm">
                {formError}
              </div>
            )}

            <form className="grid gap-3" onSubmit={onSubmit}>
              {(mode === 'create' || mode === 'edit') && (
                <>
                  <div>
                    <label className="block text-sm text-slate-600 mb-1">Nombre *</label>
                    <input
                      value={mode==='create' ? createForm.nombre : editForm.nombre}
                      onChange={(e)=> mode==='create'
                        ? setCreateForm(s=>({...s, nombre: e.target.value}))
                        : setEditForm(s=>({...s, nombre: e.target.value}))
                      }
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                      maxLength={150}
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm text-slate-600 mb-1">Descripción</label>
                    <input
                      value={mode==='create' ? createForm.descripcion : editForm.descripcion}
                      onChange={(e)=> mode==='create'
                        ? setCreateForm(s=>({...s, descripcion: e.target.value}))
                        : setEditForm(s=>({...s, descripcion: e.target.value}))
                      }
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </div>

                  <div>
                    <label className="block text-sm text-slate-600 mb-1">Precio *</label>
                    <input
                      value={mode==='create' ? createForm.precio : editForm.precio}
                      onChange={(e)=> mode==='create'
                        ? setCreateForm(s=>({...s, precio: e.target.value}))
                        : setEditForm(s=>({...s, precio: e.target.value}))
                      }
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                      inputMode="decimal"
                      required
                    />
                  </div>
                </>
              )}

              {mode === 'create' && (
                <div>
                  <label className="block text-sm text-slate-600 mb-1">Stock inicial *</label>
                  <input
                    value={createForm.cantidad}
                    onChange={(e)=> setCreateForm(s=>({...s, cantidad: e.target.value}))}
                    className="w-full rounded-md border border-slate-300 px-3 py-2"
                    inputMode="numeric"
                    required
                  />
                </div>
              )}

              {mode === 'stock' && (
                <>
                  <div className="text-sm text-slate-600">
                    Producto: <span className="font-medium">{selected?.nombre}</span> (stock actual: {selected?.cantidad})
                  </div>
                  <div>
                    <label className="block text-sm text-slate-600 mb-1">Entrada de stock *</label>
                    <input
                      value={stockForm.cantidad}
                      onChange={(e)=> setStockForm({ cantidad: e.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                      inputMode="numeric"
                      placeholder="Ej: 10"
                      required
                    />
                  </div>
                </>
              )}

              <div className="flex items-center justify-end gap-2 mt-2">
                <button
                  type="button"
                  onClick={closeModal}
                  className="px-3 py-2 rounded-md border"
                  disabled={submitting}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-3 py-2 rounded-md bg-slate-900 text-white hover:bg-slate-800 disabled:opacity-60"
                  disabled={submitting}
                >
                  {submitting ? 'Guardando...' :
                    mode === 'create' ? 'Crear' :
                    mode === 'edit' ? 'Guardar' : 'Cargar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
