import { Outlet } from 'react-router-dom'
import { Navbar } from './Navbar' 

export default function AppLayout() {
  return (
    <div className="min-h-dvh bg-slate-50">
      <Navbar />
      <main className="container mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
