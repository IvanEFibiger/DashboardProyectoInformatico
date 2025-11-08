import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { getToken } from './localAuth'

export function ProtectedRoute() {
  const location = useLocation()
  const isAuthed = Boolean(getToken())
  if (!isAuthed) return <Navigate to="/login" state={{ from: location }} replace />
  return <Outlet />
}
