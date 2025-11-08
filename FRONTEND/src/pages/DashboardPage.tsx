// src/pages/DashboardPage.tsx
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'           
import { getUserId } from '../security/localAuth'
import { DashboardService } from '../services/dashboard.service'
import type { MovimientoReciente } from '../services/dashboard.service'


const CRIT_THRESHOLD = 3


interface LowStockItem { id:number; nombre:string; cantidad:number }

export function DashboardPage() {
  const userId = getUserId() as string
  const navigate = useNavigate()                        

  
  const ROUTES = {                                      
    nuevaFactura: '/facturas/',  
    nuevoCliente: '/clientes?new=1',
    nuevoProducto: '/productos?new=1'
  }

  
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [ingresos, setIngresos] = useState('0.00')
  const [cantFact, setCantFact] = useState(0)
  const [prodTop, setProdTop] = useState('-')
  const [cantClientes, setCantClientes] = useState(0)
  const [rankProds, setRankProds] = useState<any[]>([])
  const [rankServs, setRankServs] = useState<any[]>([])
  const [rankClientes, setRankClientes] = useState<any[]>([])
  const [lowStock, setLowStock] = useState<LowStockItem[]>([])
  const [outOfStock, setOutOfStock] = useState(0)

  
  const [movimientos, setMovimientos] = useState<MovimientoReciente[]>([])

  
  const [range, setRange] = useState<'mes'|'trim'|'anio'|'todo'>('mes')
  const [limitLow, setLimitLow] = useState(5)

  useEffect(() => {
    let alive = true
    setLoading(true)
    setError(null)

    ;(async () => {
      try {
        if (!userId) throw new Error('Sin userId')
        console.debug('[Dashboard] fetching…', { userId, limitLow, range })
        const [t, f, p, c, rp, rs, rc, ls, movs] = await Promise.all([
          DashboardService.ingresosTotales(userId, range as any),
          DashboardService.cantidadFacturas(userId, range as any),
          DashboardService.prodMasVendido(userId, range as any),
          DashboardService.cantidadClientes(userId),
          DashboardService.rankingProductos(userId, range as any),
          DashboardService.rankingServicios(userId, range as any),
          DashboardService.rankingClientes(userId, range as any),
          DashboardService.lowStock(userId, limitLow),
          DashboardService.movimientosRecientes(userId, range as any, 10, 0),
        ])
        if (!alive) return

        setIngresos(parseFloat(String(t?.total_facturas_usuario ?? 0)).toFixed(2))
        setCantFact(f?.cantidad_facturas_usuario ?? 0)
        setProdTop(p?.producto_mas_vendido ?? '-')
        setCantClientes(c?.cantidad_clientes ?? 0)
        setRankProds(rp ?? [])
        setRankServs(rs ?? [])
        setRankClientes(rc ?? [])
        setLowStock(ls?.bajos ?? [])
        setOutOfStock(ls?.outOfStock ?? 0)
        setMovimientos(movs ?? [])
      } catch (e:any) {
        if (!alive) return
        console.error('[Dashboard] fetch error', e)
        setError(e?.message || 'No se pudo cargar el dashboard')
        setIngresos('0.00'); setCantFact(0); setProdTop('-'); setCantClientes(0)
        setRankProds([]); setRankServs([]); setRankClientes([])
        setLowStock([]); setOutOfStock(0)
        setMovimientos([])
      } finally {
        if (alive) setLoading(false)
      }
    })()

    return () => { alive = false }
  }, [userId, limitLow, range])

  const low = useMemo(
    () => (lowStock || []).filter(i => (i?.cantidad ?? 0) <= limitLow),
    [lowStock, limitLow]
  )

  
  const stockCritico = useMemo(
    () => low.filter(i => i.cantidad <= CRIT_THRESHOLD).length,
    [low]
  )

  const ingresosHint = range === 'todo' ? 'acumulado' : `rango: ${range}`

  
  const chartProds = useMemo(
    () => (rankProds || []).slice(0,5).map((p:any)=>({ name: p.nombre_producto, value: p.cantidad_vendida })),
    [rankProds]
  )
  const chartServs = useMemo(
    () => (rankServs || []).slice(0,5).map((s:any)=>({ name: s.nombre_servicio, value: s.cantidad_vendida })),
    [rankServs]
  )

  return (
    <div className="container-default py-6 sm:py-8">
      {}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Dashboard</h1>
          <p className="text-slate-500 text-sm">Resumen de actividad y métricas clave</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-2">
          <RangeTabs value={range} onChange={setRange} />
          <button
            className="btn-primary"
            onClick={() => {
              setLimitLow(prev => prev) 
              window.location.reload()
            }}
          >
            <span className="material-symbols-outlined">refresh</span>Actualizar
          </button>
        </div>
      </div>

      {}
      <div className="grid gap-3 xs:grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
        {loading ? (
          <>
            <KpiSkeleton/><KpiSkeleton/><KpiSkeleton/><KpiSkeleton/><KpiSkeleton/>
          </>
        ) : (
          <>
            <KpiCard title="Ingresos" value={`$ ${igresosFmt(ingresos)}`} hint={ingresosHint} icon="payments" accent="emerald"/>
            <KpiCard title="Facturas" value={String(cantFact)} hint="emitidas" icon="receipt_long" accent="indigo"/>
            <KpiCard title="Prod. más vendido" value={prodTop} hint="ranking" icon="sell" accent="amber"/>
            <KpiCard title="Clientes" value={String(cantClientes)} hint="activos" icon="group" accent="rose"/>
            <KpiCard
              title="Stock bajo"
              value={`${low.length}${outOfStock ? ` (+${outOfStock} sin)` : ''}`}
              hint={`${stockCritico} críticos (≤ ${CRIT_THRESHOLD})`}
              icon="inventory_2"
              accent="slate"
            />
          </>
        )}
      </div>

      {}
      <div className="grid lg:grid-cols-3 gap-6 mt-6">
        {}
        <div className="lg:col-span-2 space-y-6">
          <Card title={`Productos con stock bajo (≤ ${limitLow})`} right={
            <div className="flex items-center gap-2 text-sm">
              <label className="text-slate-500">Umbral</label>
              <input
                type="number"
                min={1}
                className="w-16 rounded-lg border border-slate-200 px-2 py-1"
                value={limitLow}
                onChange={e => setLimitLow(Math.max(1, parseInt(e.target.value || '1', 10)))}
              />
            </div>
          }>
            {loading ? <TableSkeleton rows={5} cols={3}/> : (
              low.length === 0 ? (
                <EmptyState icon="inventory" title="Sin alertas de stock" subtitle="Ningún producto bajo el umbral configurado."/>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead>
                      <tr className="text-left border-b">
                        <th className="py-2 pr-6">Producto</th>
                        <th className="py-2 pr-6">Stock</th>
                        <th className="py-2 pr-6">Estado</th>
                      </tr>
                    </thead>
                    <tbody>
                      {low.slice(0, 12).map((p) => (
                        <tr key={p.id} className="border-b last:border-b-0">
                          <td className="py-2 pr-6">{p.nombre}</td>
                          <td className={`py-2 pr-6 font-medium ${p.cantidad <= 0 ? 'text-red-600' : 'text-amber-600'}`}>{p.cantidad}</td>
                          <td className="py-2 pr-6">
                            <StockBadge cantidad={p.cantidad}/>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )
            )}
          </Card>

          {}
          <Card title="Últimos movimientos" subtitle={range === 'todo' ? 'acumulado' : `rango: ${range}`}>
            {loading ? (
              <TableSkeleton rows={5} cols={7}/>
            ) : movimientos.length === 0 ? (
              <EmptyState icon="list_alt" title="Sin movimientos recientes" subtitle="No hay ventas registradas en el período seleccionado."/>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="text-left border-b">
                      <th className="py-2 pr-6">Fecha</th>
                      <th className="py-2 pr-6">Tipo</th>
                      <th className="py-2 pr-6">Item</th>
                      <th className="py-2 pr-6">Cant.</th>
                      <th className="py-2 pr-6">Subtotal</th>
                      <th className="py-2 pr-6">Cliente</th>
                      <th className="py-2 pr-6">Factura</th>
                    </tr>
                  </thead>
                  <tbody>
                    {movimientos.slice(0, 10).map((m, i) => (
                      <tr key={`${m.factura_id}-${m.item_id}-${i}`} className="border-b last:border-b-0">
                        <td className="py-2 pr-6 whitespace-nowrap">{fmtFechaCorta(m.fecha)}</td>
                        <td className="py-2 pr-6">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${m.tipo === 'producto' ? 'bg-indigo-100 text-indigo-800' : 'bg-emerald-100 text-emerald-800'}`}>
                            {cap(m.tipo)}
                          </span>
                        </td>
                        <td className="py-2 pr-6">{m.item_nombre}</td>
                        <td className="py-2 pr-6">{m.cantidad}</td>
                        <td className="py-2 pr-6">${Number(m.subtotal).toFixed(2)}</td>
                        <td className="py-2 pr-6">{m.cliente}</td>
                        <td className="py-2 pr-6">#{m.factura_id}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>

        {}
        <div>
          <Card title="Accesos rápidos">
            <div className="grid gap-2">
              <QuickAction
                icon="request_quote"
                label="Nueva factura"
                onClick={() => navigate(ROUTES.nuevaFactura)}     
              />
              <QuickAction
                icon="inventory"
                label="Agregar producto"
                onClick={() => navigate(ROUTES.nuevoProducto)}     
              />
              <QuickAction
                icon="person_add"
                label="Nuevo cliente"
                onClick={() => navigate(ROUTES.nuevoCliente)}      
              />
            </div>
          </Card>

          <Card title="Indicadores rápidos" subtitle="Percentiles aproximados" >
            {loading ? (
              <div className="space-y-3">
                <BarSkeleton/><BarSkeleton/><BarSkeleton/>
              </div>
            ) : (
              <div className="space-y-4">
                <StatGauge
                  label="% productos críticos"
                  value={low.length ? Math.round((stockCritico / Math.max(1, low.length)) * 100) : 0}
                  note={`${stockCritico} / ${low.length}`}
                />
                <StatGauge label="% clientes activos (proxy)" value={Math.min(100, cantClientes)} note={`${cantClientes}`}/>
                <StatGauge label="Avance facturación (proxy)" value={Math.min(100, Math.round(parseFloat(ingresos)/1000))} note={`$ ${ingresos}`}/>
              </div>
            )}
          </Card>
        </div>
      </div>

      {}
      <div className="grid lg:grid-cols-2 gap-6 mt-6">
        <Card title="Top 5 Productos" subtitle="Por cantidad vendida">
          {loading ? <TableSkeleton rows={5} cols={2}/> : (
            chartProds.length === 0 ? (
              <EmptyState icon="bar_chart" title="Sin datos para graficar"/>
            ) : (
              <div className="w-full" style={{ height: 280 }}>
                <SvgBarChart data={chartProds} valueLabel="Unidades" />
              </div>
            )
          )}
        </Card>
        <Card title="Top 5 Servicios" subtitle="Por cantidad">
          {loading ? <TableSkeleton rows={5} cols={2}/> : (
            chartServs.length === 0 ? (
              <EmptyState icon="stacked_bar_chart" title="Sin datos para graficar"/>
            ) : (
              <div className="w-full" style={{ height: 280 }}>
                <SvgBarChart data={chartServs} valueLabel="Servicios" />
              </div>
            )
          )}
        </Card>
      </div>

      <div className="mt-6">
        <Card title="Top Clientes" subtitle="Por total gastado">
          {loading ? <TableSkeleton rows={5} cols={2}/> : (
            <SimpleTable
              headers={["Cliente", "Total"]}
              rows={(rankClientes || []).slice(0, 5).map((c) => [c.nombre_cliente, c.total_gastado])}
            />
          )}
        </Card>
      </div>

      {}
      {error && (
        <div className="mt-6 p-3 rounded-lg border border-red-200 bg-red-50 text-red-800">
          {error}
        </div>
      )}
    </div>
  )
}




function SvgBarChart({
  data,
  valueLabel='Valor',
  gridColor='#e2e8f0',
  barColors = ['#6366f1','#10b981','#f59e0b','#ef4444','#06b6d4','#a78bfa','#f97316'],
}:{
  data: { name:string; value:number }[]
  valueLabel?: string
  gridColor?: string
  barColors?: string[]
}) {
  const width = 700
  const height = 240
  const padding = { top: 20, right: 16, bottom: 50, left: 40 }

  const max = Math.max(1, ...data.map(d => Number(d.value) || 0))
  const innerW = width - padding.left - padding.right
  const innerH = height - padding.top - padding.bottom
  const barGap = 14
  const barW = Math.max(8, (innerW - barGap * (data.length - 1)) / Math.max(1, data.length))

  const yScale = (v:number) => innerH - (v / max) * innerH
  const gridLines = [0, 0.25, 0.5, 0.75, 1].map(t => ({
    y: padding.top + innerH - innerH * t,
    val: Math.round(max * t),
  }))

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="100%" role="img" aria-label="Bar chart">
      <rect x="0" y="0" width={width} height={height} fill="#fff" rx="12" />

      {gridLines.map((g, i) => (
        <g key={i}>
          <line x1={padding.left} x2={width - padding.right} y1={g.y} y2={g.y} stroke={gridColor} strokeDasharray="3 3" />
          <text x={padding.left - 8} y={g.y + 4} textAnchor="end" fontSize="10" fill="#64748b">{g.val}</text>
        </g>
      ))}

      {data.map((d, i) => {
        const x = padding.left + i * (barW + barGap)
        const y = padding.top + yScale(d.value)
        const h = innerH - yScale(d.value)
        const color = barColors[i % barColors.length]
        return (
          <g key={d.name}>
            <title>{`${d.name}: ${d.value}`}</title>
            <rect x={x} y={y} width={barW} height={h} fill={color} rx={6} />
            <text x={x + barW / 2} y={y - 6} textAnchor="middle" fontSize="11" fill="#334155" fontWeight="600">
              {d.value}
            </text>
            <text x={x + barW / 2} y={height - 12} textAnchor="middle" fontSize="11" fill="#64748b">
              {truncateLabel(d.name, 12)}
            </text>
          </g>
        )
      })}

      <text x={padding.left} y={padding.top - 6} fontSize="11" fill="#64748b" fontWeight="500">
        {valueLabel}
      </text>
    </svg>
  )
}



function igresosFmt(v:string){ return v } 
function cap(s:string){ return s ? s[0].toUpperCase() + s.slice(1) : s }
function fmtFechaCorta(iso:string){
  
  try {
    const d = new Date(iso)
    if (isNaN(d.getTime())) return iso
    const dd = String(d.getDate()).padStart(2,'0')
    const mm = String(d.getMonth()+1).padStart(2,'0')
    const yy = d.getFullYear()
    return `${dd}/${mm}/${yy}`
  } catch { return iso }
}

function truncateLabel(s:string, n:number){
  if (!s) return ''
  return s.length > n ? s.slice(0, n - 1) + '…' : s
}

function RangeTabs({ value, onChange }:{ value:'mes'|'trim'|'anio'|'todo'; onChange:(v:any)=>void }){
  const opts = [
    {key:'mes', label:'Este mes'},
    {key:'trim', label:'Trimestre'},
    {key:'anio', label:'Año'},
    {key:'todo', label:'Todo'},
  ] as const
  return (
    <div className="inline-flex rounded-xl border border-slate-200 bg-white p-1">
      {opts.map(o => (
        <button
          key={o.key}
          onClick={() => onChange(o.key)}
          className={`px-3 py-1.5 rounded-lg text-sm transition ${value===o.key? 'bg-slate-900 text-white':'text-slate-600 hover:bg-slate-50'}`}
        >{o.label}</button>
      ))}
    </div>
  )
}

function Card({ title, subtitle, right, children }:{ title:string; subtitle?:string; right?:React.ReactNode; children:React.ReactNode }){
  return (
    <div className="card">
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <div>
          <h3 className="font-semibold text-slate-900">{title}</h3>
          {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
        </div>
        {right}
      </div>
      <div className="p-4">{children}</div>
    </div>
  )
}

function KpiCard({ title, value, hint, icon, accent = 'slate' }:{ title:string; value:string; hint?:string; icon?:string; accent?: 'slate'|'emerald'|'indigo'|'amber'|'rose' }){
  const map:any = {
    slate: 'bg-slate-100 text-slate-700',
    emerald: 'bg-emerald-100 text-emerald-700',
    indigo: 'bg-indigo-100 text-indigo-700',
    amber: 'bg-amber-100 text-amber-700',
    rose: 'bg-rose-100 text-rose-700',
  }
  return (
    <div className="rounded-2xl bg-white shadow-sm border border-slate-200 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">{title}</p>
          <p className="text-2xl font-semibold text-slate-900 mt-1">{value}</p>
          {hint && <p className="text-xs text-slate-500 mt-1">{hint}</p>}
        </div>
        {icon && (
          <span className={`material-symbols-outlined text-2xl rounded-xl p-2 ${map[accent]}`}>{icon}</span>
        )}
      </div>
    </div>
  )
}

function SimpleTable({ headers, rows }:{ headers:string[]; rows:(React.ReactNode)[][] }){
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="text-left border-b">
            {headers.map((h) => (
              <th key={h} className="py-2 pr-6 text-slate-500 font-medium">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-b last:border-b-0">
              {r.map((c, j) => (
                <td key={j} className="py-2 pr-6">{c}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function EmptyState({ icon, title, subtitle }:{ icon:string; title:string; subtitle?:string }){
  return (
    <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 p-3">
      <span className="material-symbols-outlined">{icon}</span>
      <div>
        <p className="font-medium text-slate-800">{title}</p>
        {subtitle && <p className="text-sm text-slate-500">{subtitle}</p>}
      </div>
    </div>
  )
}

function StockBadge({ cantidad }:{ cantidad:number }){
  if (cantidad <= 0) return <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">Sin stock</span>
  if (cantidad <= CRIT_THRESHOLD) return <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">Crítico</span>
  return <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-700">Bajo</span>
}

function StatGauge({ label, value, note }:{ label:string; value:number; note?:string }){
  const v = Math.max(0, Math.min(100, value || 0))
  return (
    <div>
      <div className="flex items-center justify-between text-sm mb-1">
        <span className="text-slate-700 font-medium">{label}</span>
        <span className="text-slate-500">{v}%</span>
      </div>
      <div className="h-2.5 rounded-full bg-slate-100 overflow-hidden">
        <div className="h-2.5 bg-gradient-to-r from-indigo-500 to-emerald-500" style={{ width: `${v}%` }} />
      </div>
      {note && <p className="text-xs text-slate-500 mt-1">{note}</p>}
    </div>
  )
}

function QuickAction({ icon, label, onClick }:{ icon:string; label:string; onClick?:()=>void }){
  return (
    <button onClick={onClick} className="w-full inline-flex items-center gap-2 rounded-lg px-3 py-2 border border-slate-200 hover:bg-slate-50 transition">
      <span className="material-symbols-outlined">{icon}</span>
      <span className="text-sm font-medium">{label}</span>
    </button>
  )
}


function KpiSkeleton(){
  return (
    <div className="rounded-2xl bg-white shadow-sm border border-slate-200 p-4 animate-pulse">
      <div className="h-3 w-20 bg-slate-200 rounded"></div>
      <div className="h-7 w-24 bg-slate-200 rounded mt-2"></div>
      <div className="h-3 w-16 bg-slate-100 rounded mt-2"></div>
    </div>
  )
}
function BarSkeleton(){
  return (
    <div className="space-y-1 animate-pulse">
      <div className="h-3 w-32 bg-slate-200 rounded"/>
      <div className="h-2 w-full bg-slate-100 rounded"/>
    </div>
  )
}
function TableSkeleton({ rows=5, cols=3 }:{ rows?:number; cols?:number }){
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200">
      <div className="divide-y divide-slate-200 animate-pulse">
        {Array.from({ length: rows }).map((_, r) => (
          <div key={r} className="grid" style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}>
            {Array.from({ length: cols }).map((_, c) => (
              <div key={c} className="h-8 bg-slate-100"/>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}

export default DashboardPage
