"""PVBPQAE-12 · Técnica explicada y errores comunes: el botón «📘 Cómo se hace» (Marta).

Al lado de cada ejercicio (en la rutina y en la pantalla de entrenar) hay un botón que abre
una ventanita con los pasos y los errores comunes de ese ejercicio.
- Premium: ve la explicación (tabla «tecnica_ejercicios», 9_crear_tabla_tecnica.sql).
  Si todavía no está escrita, ve «Muy pronto».
- Plan gratuito: el botón sale con candado 🔒 y lleva a «Hazte Premium».

El contenido lo escribe el equipo (hoy en Supabase; más adelante, desde el panel de
administración, PVBPQAE-95).
"""
import re

import streamlit as st

from comun import cuentas

TABLA = "tecnica_ejercicios"


def nombre_base(ejercicio: str) -> str:
    """El ejercicio sin las series: «Sentadilla goblet 3x15» → «Sentadilla goblet».
    (La misma regla que usa 9_crear_tabla_tecnica.sql.)"""
    return re.sub(r"\s+\d.*$", "", ejercicio.strip()).strip()


def _explicaciones() -> dict:
    """Todas las explicaciones escritas, por nombre de ejercicio (se leen una vez por sesión)."""
    usuario = cuentas.usuario_actual()
    if "tecnica" not in usuario:
        try:
            filas = cuentas.sb().table(TABLA).select("ejercicio, pasos, errores, imagen_url").execute().data
        except Exception:
            return {}
        usuario["tecnica"] = {f["ejercicio"].lower(): f for f in filas}
    return usuario["tecnica"]


def _ir_a_premium() -> None:
    st.session_state.seccion = "suscripcion"


def _lista(texto: str) -> str:
    """Un elemento por línea → lista con viñetas."""
    lineas = [l.strip(" -•\t") for l in (texto or "").splitlines() if l.strip(" -•\t")]
    return "\n".join(f"- {l}" for l in lineas)


def boton(ejercicio: str, clave: str) -> None:
    """Botón «📘 Cómo se hace» de un ejercicio."""
    nombre = nombre_base(ejercicio)
    premium = cuentas.es_premium()
    with st.popover("📘 Cómo se hace" if premium else "🔒 Cómo se hace"):
        if not premium:
            st.markdown("**🔒 Contenido Premium**")
            st.caption("La técnica explicada de cada ejercicio es parte del plan Premium.")
            st.button("💎 Hazte Premium", key=f"tecnica_premium_{clave}", type="primary",
                      use_container_width=True, on_click=_ir_a_premium)
            return
        st.markdown(f"**{nombre}**")
        info = _explicaciones().get(nombre.lower()) or {}
        if not (info.get("pasos") or info.get("errores")):
            st.caption("Estamos preparando la explicación de este ejercicio. ¡Muy pronto!")
            return
        if info.get("imagen_url"):
            st.image(info["imagen_url"], use_container_width=True)
        if info.get("pasos"):
            st.markdown("**Cómo se hace**")
            st.markdown(_lista(info["pasos"]))
        if info.get("errores"):
            st.markdown("**Errores comunes**")
            st.markdown(_lista(info["errores"]))


def fila(ejercicio: str, clave: str) -> None:
    """Un ejercicio de la rutina con su botón a la derecha."""
    with st.container(key=f"ejercicio_{clave}"):  # estilos.py lo deja en una sola fila en el móvil
        texto, accion = st.columns([3, 2], vertical_alignment="center")
        texto.markdown(f"- {ejercicio}")
        with accion:
            boton(ejercicio, clave)
