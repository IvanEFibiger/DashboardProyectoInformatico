import { useEffect, useMemo, useState } from 'react'
import { getUserId } from '../../security/localAuth'
import { ClientesService, type Cliente } from '../../services/clientes.service'

type FormMode = 'create' | 'edit'

type FormState = {
  nombre: string
  email: string
  direccion: string
  cuit: string
}

const emptyForm: FormState = { nombre: '', email: '', direccion: '', cuit: '' }

export function ClientesPage() {
  const userId = getUserId() as string
  const [page, setPage] = useState(1)
  const [rows, setRows] = useState<Cliente[]>([])
  const [totalPages, setTotalPages] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)


  const [isOpen, setIsOpen] = useState(false)
  const [mode, setMode] = useState<FormMode>('create')
  const [selected, setSelected] = useState<Cliente | null>(null)
  const [form, setForm] = useState<FormState>(emptyForm)
  const [submitting, setSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await ClientesService.getPaged(userId, page)
      setRows(data.clients)
      setTotalPages(data.total_pages)
    } catch (e: any) {
      setError(e?.message ?? 'Error al cargar clientes')
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
    setForm(emptyForm)
    setFormError(null)
    setIsOpen(true)
  }

  const openEdit = (c: Cliente) => {
    setMode('edit')
    setSelected(c)
    setForm({
      nombre: c.nombre ?? '',
      email: c.email ?? '',
      direccion: c.direccion ?? '',
      cuit: c.cuit ?? '',
    })
    setFormError(null)
    setIsOpen(true)
  }

  const closeModal = () => {
    if (submitting) return
    setIsOpen(false)
  }

  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setForm(s => ({ ...s, [name]: value }))
  }

  const validate = (f: FormState): string | null => {
    if (!f.nombre.trim()) return 'El nombre es obligatorio.'
    if (!f.cuit.trim()) return 'El CUIT es obligatorio.'
    if (f.nombre.length > 150) return 'El nombre es demasiado largo.'
    if (f.cuit.length > 32) return 'El CUIT es demasiado largo.'
    if (f.email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(f.email)) return 'Email inválido.'
    return null
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const msg = validate(form)
    if (msg) { setFormError(msg); return }
    try {
      setSubmitting(true)
      setFormError(null)
      if (mode === 'create') {
        await ClientesService.create(userId, form)

        if (rows.length === 0 && page > 1) setPage(p => p - 1)
        else await fetchData()
      } else if (mode === 'edit' && selected) {
        await ClientesService.update(userId, selected.id, form)
        await fetchData()
      }
      setIsOpen(false)
    } catch (e: any) {
      const apiMsg = e?.response?.data?.message
      setFormError(apiMsg || e?.message || 'Error al guardar')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('¿Eliminar este cliente?')) return
    try {
      await ClientesService.remove(userId, id)
      if (rows.length === 1 && page > 1) {
        setPage(p => p - 1)
      } else {
        fetchData()
      }
    } catch (e: any) {
      alert(e?.response?.data?.message ?? e?.message ?? 'Error al eliminar')
    }
  }

  const title = useMemo(() => mode === 'create' ? 'Nuevo cliente' : 'Editar cliente', [mode])

  return (
    <div className="grid gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Clientes</h1>
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
                {['ID','Nombre','Dirección','Email','CUIT','Acciones'].map(h=> (
                  <th key={h} className="py-2 pr-6">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((c)=> (
                <tr key={c.id} className="border-b last:border-b-0">
                  <td className="py-2 pr-6">{c.id}</td>
                  <td className="py-2 pr-6">{c.nombre}</td>
                  <td className="py-2 pr-6">{c.direccion}</td>
                  <td className="py-2 pr-6">{c.email}</td>
                  <td className="py-2 pr-6">{c.cuit}</td>
                  <td className="py-2 pr-6 flex gap-2">
                    <button
                      className="px-2 py-1 rounded bg-slate-900 text-white"
                      onClick={() => openEdit(c)}
                    >
                      Editar
                    </button>
                    <button
                      className="px-2 py-1 rounded bg-red-600 text-white"
                      onClick={() => handleDelete(c.id)}
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))}

              {!loading && rows.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-sm text-slate-500">
                    No hay clientes para mostrar.
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

      {}
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
              <div>
                <label className="block text-sm text-slate-600 mb-1">Nombre *</label>
                <input
                  name="nombre"
                  value={form.nombre}
                  onChange={onChange}
                  className="w-full rounded-md border border-slate-300 px-3 py-2"
                  maxLength={150}
                  required
                />
              </div>

              <div>
                <label className="block text-sm text-slate-600 mb-1">Email</label>
                <input
                  name="email"
                  type="email"
                  value={form.email}
                  onChange={onChange}
                  className="w-full rounded-md border border-slate-300 px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm text-slate-600 mb-1">Dirección</label>
                <input
                  name="direccion"
                  value={form.direccion}
                  onChange={onChange}
                  className="w-full rounded-md border border-slate-300 px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm text-slate-600 mb-1">CUIT *</label>
                <input
                  name="cuit"
                  value={form.cuit}
                  onChange={onChange}
                  className="w-full rounded-md border border-slate-300 px-3 py-2"
                  maxLength={32}
                  required
                />
              </div>

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
                  {submitting ? 'Guardando...' : (mode === 'create' ? 'Crear' : 'Guardar')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
