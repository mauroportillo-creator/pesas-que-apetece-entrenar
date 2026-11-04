export default function Home() {
  return (
    <section className="hero">
      <p className="eyebrow">Fuerza para empezar</p>
      <h1>Escanea tu pesa. Empieza a entrenar.</h1>
      <p className="lead">
        Cada pesa lleva un código QR. Escanéalo con el móvil y entra directamente en una
        rutina pensada para ese peso y para tu nivel. Sin descargar nada.
      </p>

      <p className="lead"><strong>¿Aún no has escaneado tu pesa?</strong> Busca el código QR que lleva y ábrelo con la cámara del móvil.</p>

      <ol className="steps">
        <li><strong>Escanea</strong> el QR de tu pesa.</li>
        <li><strong>Cuéntanos</strong> tu nivel y tu objetivo.</li>
        <li><strong>Entrena</strong> con una rutina guiada paso a paso.</li>
      </ol>
    </section>
  )
}
