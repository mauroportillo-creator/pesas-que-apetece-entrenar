"""PVBPQAE-93 · Suscribirme al plan Premium (Marta).

1. «💎 Hazte Premium» (menú lateral) abre la pantalla de suscripción: qué incluye, el precio
   y los botones «Aceptar» y «Cancelar». No se paga nada: la suscripción es simulada.
2. «Aceptar» cambia el plan a Premium y regala una tarjeta para la tienda (función
   hacerme_premium() de Supabase, 8_suscripcion_premium.sql). «Cancelar» vuelve a Inicio.
3. La zona Premium solo la ve quien es Premium: su tarjeta regalo y los accesos a la técnica
   explicada (PVBPQAE-12) y la alimentación (PVBPQAE-98).
   El resto de la web (rutinas, temporizador, mi progreso, tienda…) es igual para todos.
"""
from datetime import date

import streamlit as st

from comun import cuentas, estilos

PRECIO = "4,99 €/mes"
VENTAJAS = [
    ("🏋️", "Técnica explicada", "Cómo se hace cada ejercicio y los errores más comunes."),
    ("🥗", "Alimentación", "Consejos de alimentación según tu objetivo."),
    ("🎁", "Tarjeta regalo de 10 €", "Para usarla en la tienda de pesas."),
]
# Contenido de la zona Premium: (icono, título, texto, historia). Cuando MF termine la 12 y la 98,
# cada apartado abrirá su pantalla; mientras tanto se muestra «Muy pronto».
CONTENIDO = [
    ("🏋️", "Técnica explicada", "Aprende a hacer cada ejercicio sin lesionarte.", "PVBPQAE-12"),
    ("🥗", "Alimentación", "Consejos pensados para tu objetivo.", "PVBPQAE-98"),
]


# ---------------------------------------------------------------- acciones (botones)
def _aceptar() -> None:
    error = cuentas.hacerme_premium()
    if error:
        st.session_state.error_premium = error
        return
    st.session_state.recien_premium = True
    st.session_state.seccion = "zona_premium"


def _cancelar() -> None:
    st.session_state.seccion = "inicio"


# ---------------------------------------------------------------- lo que se ve
def boton_menu(seccion: str, ir_a_seccion) -> None:
    """Botón del menú lateral: «Hazte Premium» o, si ya lo es, «Zona Premium»."""
    if cuentas.es_premium():
        texto, destino = "💎 Zona Premium", "zona_premium"
    else:
        texto, destino = "💎 Hazte Premium", "suscripcion"
    st.button(texto, key="lat_premium", use_container_width=True,
              type="primary" if seccion == destino else "secondary",
              on_click=ir_a_seccion, args=(destino,))


def etiqueta_plan() -> str:
    """Etiqueta del plan para el menú lateral."""
    return "Plan Premium" if cuentas.es_premium() else "Plan gratuito"


def _tarjeta_html(tarjeta: dict) -> str:
    importe = f"{float(tarjeta['importe']):.0f} €"
    estado = "Ya usada" if tarjeta.get("usada") else "Sin usar · úsala en la tienda"
    return (
        '<div style="border:2px dashed #EA580C;border-radius:16px;padding:1rem;text-align:center;'
        'background:#FFF7ED;margin:.6rem 0 1rem">'
        f'<div style="font-size:.85rem;color:#9A3412">🎁 Tarjeta regalo</div>'
        f'<div style="font-size:2rem;font-weight:800;color:#C2410C;line-height:1.2">{importe}</div>'
        f'<div style="font-family:monospace;font-size:1.15rem;font-weight:700;letter-spacing:.08em;'
        f'color:#1F2937">{tarjeta["codigo"]}</div>'
        f'<div style="font-size:.8rem;color:#9A3412;margin-top:.3rem">{estado}</div></div>'
    )


def mostrar_suscripcion() -> None:
    """Pantalla de suscripción (escenarios 1 y 2)."""
    if cuentas.es_premium():
        mostrar_zona()
        return
    estilos.titulo("Hazte Premium 💎", "Entrena mejor con todo el contenido de la app.")
    st.markdown(
        '<div class="tarjeta-pesa"><div class="peso" style="font-size:2.4rem">'
        f'{PRECIO}</div><div class="etiqueta">Sin permanencia</div></div>',
        unsafe_allow_html=True,
    )
    for icono, titulo, texto in VENTAJAS:
        st.markdown(
            f'<div class="ventaja"><div class="ventaja-icono">{icono}</div><div>'
            f'<div class="ventaja-titulo">{titulo}</div><div class="ventaja-texto">{texto}</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )
    st.write("")
    if error := st.session_state.pop("error_premium", None):
        st.error(error)
    st.button("Aceptar", key="premium_aceptar", type="primary", use_container_width=True,
              on_click=_aceptar)
    st.button("Cancelar", key="premium_cancelar", use_container_width=True, on_click=_cancelar)
    st.caption("No se cobra nada: el pago es simulado.")


def mostrar_zona() -> None:
    """Zona Premium (escenario 3): solo para quien tiene el plan Premium."""
    if not cuentas.es_premium():
        mostrar_suscripcion()
        return
    if st.session_state.pop("recien_premium", False):
        st.success("🎉 ¡Ya eres Premium! Te hemos regalado una tarjeta para la tienda.")

    usuario = cuentas.usuario_actual()
    desde = usuario.get("fecha_suscripcion")
    if desde:
        desde = date.fromisoformat(str(desde)).strftime("%d/%m/%Y")
    estilos.titulo("Zona Premium 💎", f"Premium desde el {desde}." if desde else None)

    tarjeta = cuentas.tarjeta_regalo()
    if tarjeta:
        st.markdown(_tarjeta_html(tarjeta), unsafe_allow_html=True)

    st.subheader("Tu contenido Premium")
    for icono, titulo, texto, historia in CONTENIDO:
        with st.container(border=True):
            st.markdown(f"**{icono} {titulo}**  \n{texto}")
            st.caption("Muy pronto")
