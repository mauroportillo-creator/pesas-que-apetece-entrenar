import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { supabase, configurado } from '../lib/supabase.js'

/*
  Listado de pesas: /pesas
  Sirve para ver todas las pesas disponibles y entrar en cada una sin tener
  que escanear el QR (útil para probar y para la demo).
*/
export default function Pesas() {
  const [estado, setEstado] = useState('cargando') // cargando | ok | error
  const [pesas, setPesas] = useState([])

  useEffect(() => {
    let cancelado = false

    async function cargar() {
      if (!configurado) return setEstado('error')
      const { data, error } = await supabase
        .from('pesas')
        .select('codigo, peso_kg, rutinas ( id, nombre, nivel )')
        .order('peso_kg', { ascending: true })

      if (cancelado) return
      if (error) return setEstado('error')
      setPesas(data ?? [])
      setEstado('ok')
    }

    cargar()
    return () => { cancelado = true }
  }, [])

  if (estado === 'cargando') return <p className="aviso" role="status">Cargando pesas…</p>

  if (estado === 'error') {
    return (
      <section className="card">
        <h1>No hemos podido cargar las pesas</h1>
        <p>
          {configurado
            ? 'Hubo un problema al conectar. Inténtalo de nuevo en unos minutos.'
            : 'La web aún no está conectada a la base de datos (faltan las variables VITE_SUPABASE_URL y VITE_SUPABASE_KEY).'}
        </p>
        <Link to="/" className="btn btn-ghost">Volver al inicio</Link>
      </section>
    )
  }

  return (
    <section>
      <p className="eyebrow">Nuestras pesas</p>
      <h1>Elige tu pesa</h1>
      <p className="lead">Cada pesa tiene su rutina. Al escanear su QR llegas directamente a ella.</p>

      {pesas.length === 0 ? (
        <p className="aviso">Todavía no hay pesas registradas.</p>
      ) : (
        <ul className="lista-pesas">
          {pesas.map((p) => (
            <li key={p.codigo}>
              <Link to={`/p/${p.codigo}`} className="fila-pesa">
                <span className="mini-badge"><b>{p.peso_kg}</b> kg</span>
                <span className="fila-texto">
                  <strong>{p.rutinas ? p.rutinas.nombre : 'Sin rutina asociada'}</strong>
                  {p.rutinas && <small>Nivel {p.rutinas.nivel.toLowerCase()}</small>}
                </span>
                <span aria-hidden="true" className="flecha">›</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
