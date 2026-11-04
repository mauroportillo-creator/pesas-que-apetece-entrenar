import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { supabase, configurado } from '../lib/supabase.js'

/*
  Página de destino de cada pesa: /p/{código}
  El QR de la pesa lleva aquí. Busca el código en la tabla `pesas` de Supabase
  y muestra el peso y la rutina asociada (tabla `rutinas`).
*/
export default function Pesa() {
  const { codigo } = useParams()
  const [estado, setEstado] = useState('cargando') // cargando | ok | noEncontrada | error
  const [pesa, setPesa] = useState(null)

  useEffect(() => {
    let cancelado = false

    async function cargar() {
      if (!configurado) {
        setEstado('error')
        return
      }
      setEstado('cargando')
      const { data, error } = await supabase
        .from('pesas')
        .select('codigo, peso_kg, rutinas ( id, nombre, nivel )')
        .eq('codigo', codigo)
        .maybeSingle()

      if (cancelado) return
      if (error) return setEstado('error')
      if (!data) return setEstado('noEncontrada')
      setPesa(data)
      setEstado('ok')
    }

    cargar()
    return () => { cancelado = true }
  }, [codigo])

  if (estado === 'cargando') {
    return <p className="aviso" role="status">Buscando tu pesa…</p>
  }

  if (estado === 'noEncontrada') {
    return (
      <section className="card">
        <h1>No reconocemos este código</h1>
        <p>El código <code>{codigo}</code> no corresponde a ninguna pesa. Revisa que el QR no esté dañado.</p>
        <Link to="/" className="btn btn-primary">Volver al inicio</Link>
      </section>
    )
  }

  if (estado === 'error') {
    return (
      <section className="card">
        <h1>No hemos podido cargar tu pesa</h1>
        <p>
          {configurado
            ? 'Hubo un problema al conectar. Inténtalo de nuevo en unos minutos.'
            : 'La web aún no está conectada a la base de datos (faltan las variables VITE_SUPABASE_URL y VITE_SUPABASE_KEY).'}
        </p>
        <Link to="/" className="btn btn-ghost">Volver al inicio</Link>
      </section>
    )
  }

  const rutina = pesa.rutinas
  return (
    <section className="card pesa">
      <div className="peso-badge" aria-label={`${pesa.peso_kg} kilos`}>
        <span className="peso-num">{pesa.peso_kg}</span>
        <span className="peso-unit">kg</span>
      </div>

      <p className="eyebrow">Tu pesa</p>
      {rutina ? (
        <>
          <h1>{rutina.nombre}</h1>
          <p className="chip">Nivel {rutina.nivel.toLowerCase()}</p>
          <p className="lead">Esta rutina está pensada para la pesa de {pesa.peso_kg} kg que tienes en la mano.</p>
          <Link to={`/rutina/${rutina.id}`} className="btn btn-primary btn-block">Empezar rutina</Link>
        </>
      ) : (
        <>
          <h1>Pesa de {pesa.peso_kg} kg</h1>
          <p className="lead">Esta pesa todavía no tiene una rutina asociada.</p>
        </>
      )}

      {/* Entrada de cuenta: Mauro (registro/login) usa `state.volver` para devolver aquí a la persona */}
      <div className="cuenta">
        <p className="cuenta-txt">¿Primera vez? Crea tu cuenta para guardar tu progreso.</p>
        <Link to="/registro" state={{ volver: `/p/${codigo}` }} className="btn btn-ghost btn-block">Crear cuenta</Link>
        <Link to="/login" state={{ volver: `/p/${codigo}` }} className="link-sec">Ya tengo cuenta</Link>
      </div>
    </section>
  )
}
