import { Routes, Route, Link } from 'react-router-dom'
import Home from './pages/Home.jsx'
import Pesa from './pages/Pesa.jsx'
import Pesas from './pages/Pesas.jsx'
import Placeholder from './pages/Placeholder.jsx'

/*
  MAPA DE PANTALLAS
  Cada pantalla vive en su propio archivo dentro de src/pages/.
  Para añadir la tuya: sustituye el <Placeholder> de tu ruta por tu componente
  (créalo en src/pages/) y no toques el resto.
*/
export default function App() {
  return (
    <div className="app">
      <header className="topbar">
        <Link to="/" className="brand">
          <span className="brand-dot" aria-hidden="true" />
          Pesas que apetece enseñar
        </Link>
      </header>

      <main className="content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/pesas" element={<Pesas />} />
          <Route path="/p/:codigo" element={<Pesa />} />

          {/* ── Huecos para el equipo ── */}
          <Route
            path="/registro"
            element={<Placeholder titulo="Crear cuenta" historia="PVBPQAE-46" detalle="Registro de usuarias." />}
          />
          <Route
            path="/login"
            element={<Placeholder titulo="Iniciar sesión" historia="PVBPQAE-46" detalle="Acceso con cuenta existente." />}
          />
          <Route
            path="/onboarding"
            element={<Placeholder titulo="Cuestionario inicial" historia="PVBPQAE-27" detalle="Nivel, objetivo y días de entrenamiento." />}
          />
          <Route
            path="/rutina/:id"
            element={<Placeholder titulo="Tu rutina" historia="PVBPQAE-25" detalle="Seguir la rutina paso a paso." />}
          />
          <Route
            path="/resumen"
            element={<Placeholder titulo="Resumen y valoración" historia="PVBPQAE-31" detalle="Resumen al terminar la rutina." />}
          />
          <Route
            path="/admin"
            element={<Placeholder titulo="Panel de administración" historia="PVBPQAE-51" detalle="Generar y asociar los QR de cada pesa." />}
          />

          <Route path="*" element={<Placeholder titulo="Página no encontrada" detalle="Esta dirección no existe." volver />} />
        </Routes>
      </main>
    </div>
  )
}
