"""PVBPQAE-93 · Suscribirme al plan Premium (Marta).

1. «💎 Hazte Premium» (menú lateral) abre la pantalla de suscripción: qué incluye, el precio
   y los botones «Aceptar» y «Cancelar». No se paga nada: la suscripción es simulada.
2. «Aceptar» cambia el plan a Premium y regala una tarjeta para la tienda (función
   hacerme_premium() de Supabase, 8_suscripcion_premium.sql). «Cancelar» vuelve a Inicio.
3. Solo para Premium:
   - Zona Premium (menú lateral): la tarjeta regalo.
   - «🥗 Alimentación» (barra de arriba). Con el plan gratuito sale con candado 🔒 y lleva a
     «Hazte Premium». El contenido lo pone la PVBPQAE-98 en mostrar_alimentacion().
   - La técnica explicada va dentro de cada rutina (PVBPQAE-12).
   El resto de la web (rutinas, temporizador, mi progreso, tienda…) es igual para todos.
"""
from datetime import date

import streamlit as st

from comun import cuentas, estilos

PRECIO = "4,99 €/mes"
VENTAJAS = [
    ("🏋️", "Técnica explicada", "Dentro de cada rutina: cómo se hace cada ejercicio y los errores más comunes."),
    ("🥗", "Alimentación", "Consejos de alimentación según tu objetivo."),
    ("🎁", "Tarjeta regalo de 10 €", "Para usarla en la tienda de pesas."),
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


# ---------------------------------------------------------------- menú y barra
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


def boton_alimentacion() -> tuple[str, str]:
    """Cuadro de la barra de arriba: con candado si el plan es gratuito."""
    return ("alimentacion", "🥗 Alimentación" if cuentas.es_premium() else "🔒 Alimentación")


# ---------------------------------------------------------------- tarjeta regalo
def _tarjeta_html(tarjeta: dict, titular: str) -> str:
    importe = f"{float(tarjeta['importe']):.0f} €"
    return (
        '<div style="max-width:360px;margin:.6rem auto .4rem;aspect-ratio:1.6;border-radius:18px;'
        'padding:1.1rem 1.2rem;color:#fff;display:flex;flex-direction:column;justify-content:space-between;'
        'background:linear-gradient(135deg,#F97316 0%,#C2410C 70%,#9A3412 100%);'
        'box-shadow:0 10px 26px rgba(194,65,12,.35)">'
        '<div style="display:flex;justify-content:space-between;align-items:center">'
        '<span style="font-weight:800;font-size:.95rem">🏋️ Pesas que apetece enseñar</span>'
        '<span style="background:rgba(255,255,255,.22);border-radius:999px;padding:.1rem .6rem;'
        'font-size:.72rem;font-weight:700">💎 PREMIUM</span></div>'
        '<div style="width:42px;height:30px;border-radius:6px;'
        'background:linear-gradient(135deg,#FDE68A,#F59E0B)"></div>'
        f'<div style="font-family:monospace;font-size:1.25rem;font-weight:700;letter-spacing:.14em">'
        f'{tarjeta["codigo"]}</div>'
        '<div style="display:flex;justify-content:space-between;align-items:flex-end">'
        f'<div><div style="font-size:.7rem;opacity:.8;text-transform:uppercase;letter-spacing:.08em">'
        f'Tarjeta regalo</div><div style="font-weight:600">{titular}</div></div>'
        f'<div style="font-size:2rem;font-weight:800;line-height:1">{importe}</div></div></div>'
    )


# ---------------------------------------------------------------- pantallas
def mostrar_suscripcion(aviso: str | None = None) -> None:
    """Pantalla de suscripción (escenarios 1 y 2)."""
    estilos.titulo("Hazte Premium 💎", "Entrena mejor con todo el contenido de la app.")
    if aviso:
        st.info(aviso)
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


def mostrar_zona(ir_a_seccion) -> None:
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
        titular = f"{usuario.get('nombre', '')} {usuario.get('apellidos', '')}".strip()
        st.markdown(_tarjeta_html(tarjeta, titular), unsafe_allow_html=True)
        if tarjeta.get("usada"):
            st.caption("Esta tarjeta ya se ha usado.")
        else:
            st.markdown("<div style='text-align:center;opacity:.75;font-size:.9rem'>"
                        "Sin usar · úsala en la tienda al comprar tus pesas</div>",
                        unsafe_allow_html=True)
            st.button("🛍️ Ir a la tienda", key="premium_tienda", type="primary",
                      use_container_width=True, on_click=ir_a_seccion, args=("tienda",))

    st.write("")
    st.info("🏋️ **Técnica explicada:** la encontrarás dentro de cada rutina.  \n"
            "🥗 **Alimentación:** en el botón de la barra de arriba.")


def mostrar_alimentacion() -> None:
    """«🥗 Alimentación» (barra de arriba). Solo Premium; el contenido es de la PVBPQAE-98."""
    if not cuentas.es_premium():
        mostrar_suscripcion("🔒 La alimentación es parte del plan Premium.")
        return
    estilos.titulo("Alimentación 🥗", "Consejos de alimentación según tu objetivo.")
    st.info("Muy pronto.")  # PVBPQAE-98: aquí va el contenido de alimentación
