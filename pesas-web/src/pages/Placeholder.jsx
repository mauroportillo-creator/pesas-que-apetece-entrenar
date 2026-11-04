import { Link } from 'react-router-dom'

// Pantalla provisional. Cada persona la sustituye por la suya (ver README).
export default function Placeholder({ titulo, historia, detalle, volver }) {
  return (
    <section className="card">
      {historia && <p className="eyebrow">En construcción · {historia}</p>}
      <h1>{titulo}</h1>
      <p className="lead">{detalle}</p>
      {!volver && <p className="nota">Esta pantalla la añadirá el equipo en su historia de Jira.</p>}
      <Link to="/" className="btn btn-ghost">Volver al inicio</Link>
    </section>
  )
}
