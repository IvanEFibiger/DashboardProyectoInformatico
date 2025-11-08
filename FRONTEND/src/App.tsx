import { Routes, Route } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import LandingPage from './pages/LandingPage'
import { LoginPage } from './pages/auth/LoginPage'
import { ProtectedRoute } from './security/ProtectedRoute'
import { DashboardPage } from './pages/DashboardPage'
import { ClientesPage } from './pages/clientes/ClientesPage'
import { ProductosPage } from './pages/productos/ProductosPage'
import { ServiciosPage } from './pages/servicios/ServiciosPage'
import { FacturasPage } from './pages/facturas/FacturasPage'
import { NotFoundPage } from './pages/NotFoundPage'

export default function App() {
  return (
    <Routes>
      {}
      <Route element={<AppLayout />}>
        {}
        <Route index element={<LandingPage />} />
        <Route path="login" element={<LoginPage />} />

        {}
        <Route element={<ProtectedRoute />}>
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="clientes" element={<ClientesPage />} />
          <Route path="productos" element={<ProductosPage />} />
          <Route path="servicios" element={<ServiciosPage />} />
          <Route path="facturas" element={<FacturasPage />} />
        </Route>

        {}
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
