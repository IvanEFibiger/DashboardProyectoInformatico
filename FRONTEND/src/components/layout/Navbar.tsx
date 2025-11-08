import { NavLink, Link, useNavigate } from 'react-router-dom'
import { getUsername, getToken, clearAuth } from '../../security/localAuth'

export function Navbar() {
  const navigate = useNavigate()
  const username = getUsername()
  const isLogged = Boolean(getToken())

  const onLogout = () => {
    clearAuth()
    navigate('/login')
  }

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `hover:opacity-80 ${isActive ? 'underline underline-offset-4' : ''}`

  return (
    <nav className="bg-slate-900 text-white">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <Link to={isLogged ? '/dashboard' : '/'} className="font-semibold tracking-wide">
          Inicio
        </Link>

        <div className="flex items-center gap-4">
          {isLogged ? (
            <>
              <NavLink to="/clientes" className={linkClass}>Clientes</NavLink>
              <NavLink to="/productos" className={linkClass}>Productos</NavLink>
              <NavLink to="/servicios" className={linkClass}>Servicios</NavLink>
              <NavLink to="/facturas" className={linkClass}>Facturas</NavLink>
              <span className="text-sm opacity-80">{username}</span>
              <button onClick={onLogout} className="rounded-md bg-white/10 px-3 py-1 hover:bg-white/20">
                Salir
              </button>
            </>
          ) : (
            <NavLink to="/login" className={linkClass}>Login</NavLink>
          )}
        </div>
      </div>
    </nav>
  )
}
