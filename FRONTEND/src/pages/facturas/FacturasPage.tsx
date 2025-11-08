// src/pages/facturas/FacturasPage.tsx
import { useEffect, useMemo, useState } from 'react'
import { FacturasService } from '../../services/facturas.service'
import { ClientesService, type Cliente } from '../../services/clientes.service'
import { ProductosService, type Producto } from '../../services/productos.service'
import { ServiciosService, type Servicio } from '../../services/servicios.service'
import { getUserId } from '../../security/localAuth'
import { EMISOR } from '../../config/emisor'

type Item = {
  tipo: 'producto' | 'servicio'
  id_producto?: string
  id_servicio?: string
  cantidad: string
}

type NuevaFacturaForm = {
  fecha_emision: string
  id_clientes: string
  items: Item[]
}

function todayISODateTimeLocal() {
  const d = new Date()
  d.setSeconds(0, 0)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}


function escapeHTML(s: any) {
  return String(s ?? '')
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;')
}


function fmtMoney(n: number) {
  if (!Number.isFinite(n)) return '$ 0,00'
  return n.toLocaleString('es-AR', { style: 'currency', currency: 'ARS', minimumFractionDigits: 2 })
}


function pad(n: number, size: number) {
  const s = String(n)
  return s.length >= size ? s : ('0'.repeat(size - s.length) + s)
}

export function FacturasPage(){
  const userId = getUserId() as string


  const [page, setPage] = useState(1)
  const [rows, setRows] = useState<any[]>([])
  const [totalPages, setTotalPages] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)


  const [open, setOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)


  const [clientes, setClientes] = useState<Cliente[]>([])
  const [productos, setProductos] = useState<Producto[]>([])
  const [servicios, setServicios] = useState<Servicio[]>([])
  const [loadingCats, setLoadingCats] = useState(false)
  const [catsError, setCatsError] = useState<string | null>(null)

  const [form, setForm] = useState<NuevaFacturaForm>({
    fecha_emision: todayISODateTimeLocal(),
    id_clientes: '',
    items: [{ tipo: 'producto', id_producto: '', cantidad: '1' }],
  })

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await FacturasService.getPaged(userId, page)
      setRows(data.facturas_detalles || [])
      setTotalPages(data.total_pages || 1)
    } catch (e: any) {
      setError(e?.response?.data?.message || e?.message || 'Error al cargar facturas')
    } finally {
      setLoading(false)
    }
  }

  useEffect(()=>{ fetchData() },[userId,page])


  const loadAllClientes = async () => {
    const acc: Cliente[] = []
    for (let p = 1; p <= 50; p++) {
      const { clients, total_pages } = await ClientesService.getPaged(userId, p)
      if (Array.isArray(clients)) acc.push(...clients)
      if (p >= (total_pages ?? 1)) break
    }
    return acc
  }
  const loadAllProductos = async () => {
    const acc: Producto[] = []
    for (let p = 1; p <= 50; p++) {
      const { products, total_pages } = await ProductosService.getPaged(userId, p)
      if (Array.isArray(products)) acc.push(...products)
      if (p >= (total_pages ?? 1)) break
    }
    return acc
  }
  const loadAllServicios = async () => {
    const acc: Servicio[] = []
    for (let p = 1; p <= 50; p++) {
      const { service, total_pages } = await ServiciosService.getPaged(userId, p)
      if (Array.isArray(service)) acc.push(...service)
      if (p >= (total_pages ?? 1)) break
    }
    return acc
  }

  const loadCatalogos = async () => {
    try {
      setLoadingCats(true)
      setCatsError(null)
      const [cls, prods, servs] = await Promise.all([
        loadAllClientes(),
        loadAllProductos(),
        loadAllServicios(),
      ])
      setClientes(cls.filter(c => c.activo === undefined || c.activo === 1))
      setProductos(prods.filter(p => p.activo === undefined || p.activo === 1))
      setServicios(servs.filter(s => s.activo === undefined || s.activo === 1))
    } catch (e: any) {
      setCatsError(e?.response?.data?.message || e?.message || 'Error al cargar catálogos')
    } finally {
      setLoadingCats(false)
    }
  }

  const openNueva = async () => {
    setForm({
      fecha_emision: todayISODateTimeLocal(),
      id_clientes: '',
      items: [{ tipo: 'producto', id_producto: '', cantidad: '1' }],
    })
    setFormError(null)
    setOpen(true)
    await loadCatalogos()
  }

  const closeNueva = () => { if (!submitting) setOpen(false) }

  const addItem = () => {
    setForm(f => ({
      ...f,
      items: [...f.items, { tipo: 'producto', id_producto: '', cantidad: '1' }]
    }))
  }

  const removeItem = (idx: number) => {
    setForm(f => ({
      ...f,
      items: f.items.filter((_, i) => i !== idx)
    }))
  }

  const updateItem = (idx: number, patch: Partial<Item>) => {
    setForm(f => {
      const items = [...f.items]
      items[idx] = { ...items[idx], ...patch }
      if (patch.tipo === 'producto') items[idx].id_servicio = ''
      if (patch.tipo === 'servicio') items[idx].id_producto = ''
      return { ...f, items }
    })
  }


  const { prodById, servById } = useMemo(() => {
    return {
      prodById: new Map(productos.map(p => [String(p.id), p])),
      servById: new Map(servicios.map(s => [String(s.id), s])),
    }
  }, [productos, servicios])

  const itemsCalc = useMemo(() => {
    return form.items.map((it) => {
      const qty = Number(it.cantidad ?? '0') || 0
      let precio = 0
      let desc = ''
      if (it.tipo === 'producto' && it.id_producto) {
        const p = prodById.get(String(it.id_producto))
        if (p) { precio = Number(p.precio) || 0; desc = p.nombre }
      } else if (it.tipo === 'servicio' && it.id_servicio) {
        const s = servById.get(String(it.id_servicio))
        if (s) { precio = Number(s.precio) || 0; desc = s.nombre }
      }
      const subtotal = Math.max(0, qty * precio)
      return { ...it, qty, precio, desc, subtotal }
    })
  }, [form.items, prodById, servById])

  const totales = useMemo(() => {
    const subtotal = itemsCalc.reduce((a, b) => a + (Number(b.subtotal) || 0), 0)
    return { subtotal, total: subtotal }
  }, [itemsCalc])

  const validar = (f: NuevaFacturaForm): string | null => {
    if (!f.id_clientes.trim()) return 'Cliente es obligatorio.'
    if (f.items.length === 0) return 'Agregá al menos un renglón.'
    for (let i=0; i<f.items.length; i++) {
      const it = f.items[i]
      if (it.tipo === 'producto' && !it.id_producto?.trim()) return `Item ${i+1}: falta producto.`
      if (it.tipo === 'servicio' && !it.id_servicio?.trim()) return `Item ${i+1}: falta servicio.`
      const q = Number(it.cantidad)
      if (!Number.isFinite(q) || q <= 0) return `Item ${i+1}: cantidad inválida.`
    }
    return null
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setSubmitting(true)
      setFormError(null)
      const msg = validar(form)
      if (msg) throw new Error(msg)

      const payload = {
        fecha_emision: form.fecha_emision,
        id_clientes: Number(form.id_clientes),
        productos_servicios: form.items.map(it => ({
          cantidad: Number(it.cantidad),
          id_producto: it.tipo === 'producto' ? Number(it.id_producto) : undefined,
          id_servicio: it.tipo === 'servicio' ? Number(it.id_servicio) : undefined,
        })),
      }

      await FacturasService.create(userId, payload)
      await fetchData()
      setOpen(false)
    } catch (e: any) {
      setFormError(e?.response?.data?.message || e?.message || 'Error al crear la factura')
    } finally {
      setSubmitting(false)
    }
  }

  const handleEliminar = async (id: number) => {
    if (!confirm('¿Eliminar esta factura? Se borrarán sus detalles.')) return
    try {
      await FacturasService.remove(userId, id)
      if (rows.length === 1 && page > 1) setPage(p => p - 1)
      else fetchData()
    } catch (e: any) {
      alert(e?.response?.data?.message ?? e?.message ?? 'Error al eliminar')
    }
  }

  const handleVer = async (id: number) => {
    try {
      const data = await FacturasService.getDetalle(userId, id)
      alert(JSON.stringify(data, null, 2))
    } catch (e: any) {
      alert(e?.response?.data?.message ?? e?.message ?? 'Error al consultar')
    }
  }

 
  const handlePDF = async (id: number) => {
    try {
      const data = await FacturasService.getDetalle(userId, id)
      const w = window.open('', '_blank', 'width=980,height=900')
      if (!w) return

      const f = data?.factura ?? {}
      const c = data?.cliente ?? {}
      const detalles = data?.detalles ?? []
      const total = Number(data?.total ?? f?.total ?? 0)

      
      const nroInterno = `${EMISOR.puntoVenta}-${pad(Number(f.id ?? id), 8)}`
      const fecha = String(f.fecha_emision ?? '').replace('T', ' ').slice(0, 16) 
      const tipoComprobante = 'PROFORMA / COMPROBANTE NO FISCAL'


      const rowsHTML = detalles.map((d:any, i:number) => {
        const etiqueta = d.id_producto ? `Producto #${escapeHTML(d.id_producto)}`
                        : d.id_servicio ? `Servicio #${escapeHTML(d.id_servicio)}`
                        : 'Ítem'
        const cant = Number(d.cantidad ?? 0)
        const pu = Number(d.precio_unitario ?? 0)
        const sub = Number(d.subtotal ?? (cant * pu))
        return `
          <tr>
            <td>${i+1}</td>
            <td>${etiqueta}</td>
            <td class="num">${cant}</td>
            <td class="num">${escapeHTML(fmtMoney(pu))}</td>
            <td class="num">${escapeHTML(fmtMoney(sub))}</td>
          </tr>
        `
      }).join('')

    
      const subtotal = detalles.reduce((a:number, d:any) => {
        const cant = Number(d.cantidad ?? 0)
        const pu = Number(d.precio_unitario ?? 0)
        const sub = Number(d.subtotal ?? (cant * pu))
        return a + sub
      }, 0)

    
      const totalFinal = Number.isFinite(total) && total > 0 ? total : subtotal

      const emisorLogo = EMISOR.logoUrl
        ? `<img src="${escapeHTML(EMISOR.logoUrl)}" alt="logo" style="height:58px;object-fit:contain;" />`
        : `<div class="logo-fallback">${escapeHTML(EMISOR.nombre?.[0] ?? 'I')}</div>`

      w.document.write(`
        <html>
        <head>
          <meta charset="utf-8" />
          <title>Proforma ${escapeHTML(nroInterno)}</title>
          <style>
            @page { size: A4; margin: 18mm 14mm; }
            *{ box-sizing: border-box; }
            body{ font-family: system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial, sans-serif; color:#0f172a; }
            h1,h2,h3,p,table{ margin:0; }
            .muted{ color:#64748b; }
            .wrap{ display:flex; flex-direction:column; gap:14px; }

            .header{
              display:grid; grid-template-columns: 1fr auto; gap:16px; align-items:center; border-bottom:1px solid #e5e7eb; padding-bottom:10px;
            }
            .emisor{
              display:flex; gap:12px; align-items:center;
            }
            .logo-fallback{
              width:58px; height:58px; border-radius:12px; background:#e5e7eb; color:#111827; display:flex; align-items:center; justify-content:center;
              font-weight:700; font-size:22px;
            }
            .emisor h1{ font-size:18px; font-weight:700; }
            .emisor .small{ font-size:12px; line-height:1.25; }

            .comp-meta{
              text-align:right;
              font-size:12px;
              line-height:1.5;
            }
            .comp-type{
              font-size:14px; font-weight:700;
            }

            .blocks{
              display:grid; grid-template-columns: 1fr 1fr; gap:12px;
            }
            .block{
              border:1px solid #e5e7eb; border-radius:12px; padding:10px 12px;
            }
            .block h3{ font-size:13px; margin-bottom:6px; }
            .block .row{ font-size:12px; line-height:1.4; }

            table{ width:100%; border-collapse: collapse; }
            .items{ margin-top:6px; }
            .items th, .items td{ border:1px solid #e5e7eb; padding:8px; font-size:12px; }
            .items th{ background:#f8fafc; text-align:left; font-weight:600; }
            .num{ text-align:right; white-space:nowrap; }

            .totals{
              width:100%; margin-top:8px;
              display:grid; grid-template-columns: 1fr 260px; gap:12px; align-items:start;
            }
            .tot-card{
              border:1px solid #e5e7eb; border-radius:12px; padding:10px 12px;
            }
            .tot-card table{ width:100%; }
            .tot-card td{ padding:6px 0; font-size:12px; }
            .tot-card tr td:first-child{ color:#64748b; }
            .tot-card .grand{ border-top:1px solid #e5e7eb; font-weight:700; }

            .qr-obs{
              display:grid; grid-template-columns: 120px 1fr; gap:12px; margin-top:8px;
            }
            .qr-box{
              border:1px dashed #cbd5e1; border-radius:12px; height:120px; display:flex; align-items:center; justify-content:center; font-size:11px; color:#64748b;
              text-align:center; padding:6px;
            }
            .obs{
              border:1px solid #e5e7eb; border-radius:12px; padding:10px 12px; font-size:12px; color:#334155; min-height:120px;
            }
            .leyendas{
              font-size:11px; color:#ef4444; margin-top:6px;
            }
            .footer{
              margin-top:10px; font-size:11px; color:#64748b; text-align:center;
            }
          </style>
        </head>
        <body>
          <div class="wrap">
            <div class="header">
              <div class="emisor">
                ${emisorLogo}
                <div>
                  <h1>${escapeHTML(EMISOR.nombre)}</h1>
                  <div class="small muted">
                    ${escapeHTML(EMISOR.domicilio)}<br/>
                    CUIT: ${escapeHTML(EMISOR.cuit)} — ${escapeHTML(EMISOR.condicionIVA)}<br/>
                    ${EMISOR.email ? `Email: ${escapeHTML(EMISOR.email)} — ` : ''}${EMISOR.telefono ? `Tel: ${escapeHTML(EMISOR.telefono)}` : ''}
                  </div>
                </div>
              </div>
              <div class="comp-meta">
                <div class="comp-type">${escapeHTML(tipoComprobante)}</div>
                <div>Punto de Venta: <b>${escapeHTML(EMISOR.puntoVenta)}</b></div>
                <div>N° Interno: <b>${escapeHTML(nroInterno)}</b></div>
                <div>Fecha: <b>${escapeHTML(fecha || '')}</b></div>
                <div class="muted">Moneda: ARS — Forma de pago: A convenir</div>
              </div>
            </div>

            <div class="blocks">
              <div class="block">
                <h3>Datos del Emisor</h3>
                <div class="row">${escapeHTML(EMISOR.nombre)}</div>
                <div class="row">${escapeHTML(EMISOR.domicilio)}</div>
                <div class="row">CUIT: ${escapeHTML(EMISOR.cuit)} — ${escapeHTML(EMISOR.condicionIVA)}</div>
              </div>
              <div class="block">
                <h3>Datos del Receptor</h3>
                <div class="row">${escapeHTML(c.nombre_cliente ?? '')}</div>
                <div class="row">${escapeHTML(((c as any).domicilio_cliente ?? (c as any).domicilio ?? ''))}</div>
                <div class="row">${c.cuit_cliente ? `CUIT/CUIL/DNI: ${escapeHTML(c.cuit_cliente)}` : ''}</div>
              </div>
            </div>

            <table class="items">
              <thead>
                <tr>
                  <th style="width:36px;">#</th>
                  <th>Descripción</th>
                  <th style="width:80px;">Cantidad</th>
                  <th style="width:120px;">Precio Unit.</th>
                  <th style="width:120px;">Subtotal</th>
                </tr>
              </thead>
              <tbody>
                ${rowsHTML || `<tr><td colspan="5" class="muted" style="padding:10px;">Sin renglones</td></tr>`}
              </tbody>
            </table>

            <div class="totals">
              <div class="leyendas">
                ${((EMISOR.leyendas ?? []) as string[])
                    .map((l: string) => `<div>• ${escapeHTML(l)}</div>`)
                    .join('')}
              </div>
              <div class="tot-card">
                <table>
                  <tr>
                    <td>Subtotal</td>
                    <td class="num">${escapeHTML(fmtMoney(subtotal))}</td>
                  </tr>
                  <tr class="grand">
                    <td>Total</td>
                    <td class="num">${escapeHTML(fmtMoney(totalFinal))}</td>
                  </tr>
                </table>
              </div>
            </div>

            <div class="qr-obs">
              <div class="qr-box">
                QR (no fiscal)<br/>Solo decorativo
              </div>
              <div class="obs">
                ${escapeHTML(EMISOR.observaciones)}
              </div>
            </div>

            <div class="footer">
              Este documento es una proforma / comprobante no fiscal. No posee CAE/CAI ni código de validación AFIP.
            </div>
          </div>

          <script>window.print();</script>
        </body>
        </html>
      `)
      w.document.close()
    } catch (e: any) {
      alert(e?.response?.data?.message ?? e?.message ?? 'No se pudo generar el PDF')
    }
  }

  const tituloModal = useMemo(()=> 'Nueva factura', [])

  return (
    <div className="grid gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Facturas</h1>
        <button
          onClick={openNueva}
          className="px-3 py-2 rounded-lg bg-slate-900 text-white hover:bg-slate-800"
        >
          + Nueva
        </button>
      </div>

      <div className="rounded-2xl bg-white shadow p-4">
        {loading && <div className="text-sm mb-2">Cargando...</div>}
        {error && <div className="text-sm text-red-600 mb-2">{error}</div>}

        <table className="min-w-full text-sm">
          <thead>
            <tr className="text-left border-b">
              {['N°','Fecha','Cliente','Total','Acciones'].map(h=> <th key={h} className="py-2 pr-6">{h}</th>)}
            </tr>
          </thead>
          <tbody>
            {rows.map((f:any)=> (
              <tr key={f.factura_id} className="border-b last:border-b-0">
                <td className="py-2 pr-6">{f.factura_id}</td>
                <td className="py-2 pr-6">{f.fecha_emision}</td>
                <td className="py-2 pr-6">{f.nombre_cliente}</td>
                <td className="py-2 pr-6">{Number(f.total).toFixed(2)}</td>
                <td className="py-2 pr-6 flex gap-2">
                  <button className="px-2 py-1 rounded bg-slate-900 text-white" onClick={()=>handleVer(f.factura_id)}>Ver</button>
                  <button className="px-2 py-1 rounded bg-indigo-600 text-white" onClick={()=>handlePDF(f.factura_id)}>PDF</button>
                  <button className="px-2 py-1 rounded bg-red-600 text-white" onClick={()=>handleEliminar(f.factura_id)}>Eliminar</button>
                </td>
              </tr>
            ))}
            {!loading && rows.length === 0 && (
              <tr>
                <td colSpan={5} className="py-6 text-center text-slate-500">No hay facturas para mostrar.</td>
              </tr>
            )}
          </tbody>
        </table>

        <div className="flex items-center gap-2 justify-center mt-3">
          <button disabled={page<=1} onClick={()=>setPage(p=>p-1)} className="px-3 py-1 rounded bg-white border disabled:opacity-50">Anterior</button>
          <span className="text-sm">{page} / {totalPages}</span>
          <button disabled={page>=totalPages} onClick={()=>setPage(p=>p+1)} className="px-3 py-1 rounded bg-white border disabled:opacity-50">Siguiente</button>
        </div>
      </div>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/40" onClick={closeNueva} />
          <div className="relative z-10 w-full max-w-4xl lg:max-w-5xl rounded-2xl bg-white shadow p-5">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold">{tituloModal}</h3>
              <button onClick={closeNueva} className="text-slate-500 hover:text-slate-700">✕</button>
            </div>

            {formError && (
              <div className="mb-3 rounded-md border border-red-200 bg-red-50 text-red-700 px-3 py-2 text-sm">
                {formError}
              </div>
            )}
            {catsError && (
              <div className="mb-3 rounded-md border border-yellow-200 bg-yellow-50 text-yellow-700 px-3 py-2 text-sm">
                {catsError}
              </div>
            )}

            <form className="grid gap-4" onSubmit={onSubmit}>
              <div className="grid md:grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm text-slate-600 mb-1">Fecha y hora *</label>
                  <input
                    type="datetime-local"
                    value={form.fecha_emision}
                    onChange={(e)=>setForm(s=>({...s, fecha_emision: e.target.value}))}
                    className="w-full rounded-md border border-slate-300 px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm text-slate-600 mb-1">Cliente *</label>
                  <select
                    value={form.id_clientes}
                    onChange={(e)=>setForm(s=>({...s, id_clientes: e.target.value}))}
                    className="w-full rounded-md border border-slate-300 px-3 py-2"
                    required
                    disabled={loadingCats}
                  >
                    <option value="">— seleccionar —</option>
                    {clientes.map(c=>(
                      <option key={c.id} value={String(c.id)}>
                        {c.nombre} {c.cuit ? `(${c.cuit})` : ''}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Renglones</span>
                  <button type="button" onClick={addItem} className="text-sm px-2 py-1 rounded bg-slate-900 text-white">+ Agregar</button>
                </div>

                <div className="grid gap-2">
                  {form.items.map((it, idx)=> {
                    const calc = itemsCalc[idx]
                    return (
                      <div key={idx} className="grid md:grid-cols-12 gap-2 items-end border rounded-md p-2">
                        <div className="md:col-span-2">
                          <label className="block text-xs text-slate-600 mb-1">Tipo</label>
                          <select
                            value={it.tipo}
                            onChange={(e)=>updateItem(idx, { tipo: e.target.value as Item['tipo'] })}
                            className="w-full rounded-md border border-slate-300 px-3 py-2"
                          >
                            <option value="producto">Producto</option>
                            <option value="servicio">Servicio</option>
                          </select>
                        </div>

                        {it.tipo === 'producto' ? (
                          <div className="md:col-span-4">
                            <label className="block text-xs text-slate-600 mb-1">Producto</label>
                            <select
                              value={it.id_producto ?? ''}
                              onChange={(e)=>updateItem(idx, { id_producto: e.target.value })}
                              className="w-full rounded-md border border-slate-300 px-3 py-2"
                              disabled={loadingCats}
                            >
                              <option value="">— seleccionar —</option>
                              {productos.map(p=>(
                                <option key={p.id} value={String(p.id)}>
                                  {p.nombre} — {fmtMoney(p.precio)} {Number.isFinite(p.cantidad) ? ` (stock ${p.cantidad})` : ''}
                                </option>
                              ))}
                            </select>
                          </div>
                        ) : (
                          <div className="md:col-span-4">
                            <label className="block text-xs text-slate-600 mb-1">Servicio</label>
                            <select
                              value={it.id_servicio ?? ''}
                              onChange={(e)=>updateItem(idx, { id_servicio: e.target.value })}
                              className="w-full rounded-md border border-slate-300 px-3 py-2"
                              disabled={loadingCats}
                            >
                              <option value="">— seleccionar —</option>
                              {servicios.map(s=>(
                                <option key={s.id} value={String(s.id)}>
                                  {s.nombre} — {fmtMoney(s.precio)}
                                </option>
                              ))}
                            </select>
                          </div>
                        )}

                        <div className="md:col-span-1">
                          <label className="block text-xs text-slate-600 mb-1">Cantidad</label>
                          <input
                            value={it.cantidad}
                            onChange={(e)=>updateItem(idx, { cantidad: e.target.value })}
                            className="w-full rounded-md border border-slate-300 px-3 py-2 text-right"
                            inputMode="decimal"
                            placeholder="Ej: 1"
                          />
                        </div>

                            <div className="md:col-span-2 min-w-[120px]">
                            <label className="block text-xs text-slate-600 mb-1">P. Unit</label>
                            <div className="w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-right whitespace-nowrap">
                                {fmtMoney(calc?.precio ?? 0)}
                            </div>
                            </div>

                            <div className="md:col-span-2 min-w-[140px]">
                            <label className="block text-xs text-slate-600 mb-1">Subtotal</label>
                            <div className="w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-right font-medium whitespace-nowrap">
                                {fmtMoney(calc?.subtotal ?? 0)}
                            </div>
                            </div>

                            <div className="md:col-span-1 flex items-end">
                            <button
                                type="button"
                                onClick={() => removeItem(idx)}
                                className="h-[38px] px-3 rounded-md border flex-none w-[44px] shrink-0"
                                title="Eliminar"
                            >
                                🗑️
                            </button>
                            </div>
                      </div>
                    )
                  })}
                </div>
              </div>

              {}
              <div className="grid md:grid-cols-2 gap-3">
                <div className="rounded-xl border border-slate-200 p-3">
                  <div className="text-sm text-slate-600 mb-1">Resumen</div>
                  <div className="text-xs text-slate-500">
                    {itemsCalc.length} renglón(es) — {itemsCalc.filter(i => i.subtotal>0).length} con importe
                  </div>
                </div>
                <div className="rounded-xl border border-slate-200 p-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-600">Subtotal</span>
                    <span className="font-medium">{fmtMoney(totales.subtotal)}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm border-t mt-2 pt-2">
                    <span className="text-slate-800 font-semibold">Total</span>
                    <span className="text-slate-900 font-semibold">{fmtMoney(totales.total)}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-end gap-2">
                <button type="button" onClick={closeNueva} className="px-3 py-2 rounded-md border" disabled={submitting}>Cancelar</button>
                <button type="submit" className="px-3 py-2 rounded-md bg-slate-900 text-white disabled:opacity-60" disabled={submitting || loadingCats}>
                  {submitting ? 'Creando...' : 'Crear factura'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default FacturasPage
