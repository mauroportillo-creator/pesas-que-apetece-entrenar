"""PVBPQAE-25 · Rutinas (María Luz).

Cómo se muestra una rutina: duración, descripción y ejercicios, con el
botón para guardarla en «Mis rutinas». Se usa en Inicio, Rutinas y Mis rutinas.
"""
import streamlit as st

from comun import cuentas


def _duracion(rutina: dict) -> str:
    return f"{rutina['duracion_min']} min" if rutina.get("duracion_min") else "duración por definir"


def detalle(rutina: dict) -> None:
    """Contenido de una rutina (duración, descripción y ejercicios de la tabla `rutinas`)."""
    st.caption(f"⏱️ {_duracion(rutina)} · Nivel {rutina['nivel'].lower()} · "
               f"Pesa de {rutina.get('peso_kg') or '?'} kg")
    if rutina.get("descripcion"):
        st.write(rutina["descripcion"])
    ejercicios = [e.strip() for e in (rutina.get("ejercicios") or "").split(";") if e.strip()]
    if ejercicios:
        for ejercicio in ejercicios:
            st.markdown(f"- {ejercicio}")
    else:
        st.info("🛠️ Estamos preparando los ejercicios de esta rutina. ¡Muy pronto podrás entrenar con ella!")


def _cambiar_guardada(rutina_id: str) -> None:
    """Marca o desmarca la estrella: guarda la rutina en «Mis rutinas» o la quita."""
    if rutina_id in cuentas.usuario_actual().get("rutinas_guardadas", []):
        error = cuentas.quitar_rutina(rutina_id)
        st.toast(error or "Quitada de Mis rutinas")
    else:
        error = cuentas.guardar_rutina(rutina_id)
        st.toast(error or "Guardada en Mis rutinas ⭐")


def desplegable(rutina: dict, clave: str, abierta: bool = False) -> None:
    """Rutina en un desplegable, con una estrella a la derecha para guardarla en «Mis rutinas»."""
    guardada = rutina["id"] in cuentas.usuario_actual().get("rutinas_guardadas", [])
    contenido, estrella = st.columns([12, 1], vertical_alignment="top", gap="small")
    with contenido, st.expander(f"**{rutina['nombre']}** · {_duracion(rutina)}", expanded=abierta):
        detalle(rutina)
    estrella.button("★" if guardada else "☆", key=f"estrella_{clave}",
                    help="Quitar de Mis rutinas" if guardada else "Guardar en Mis rutinas",
                    on_click=_cambiar_guardada, args=(rutina["id"],))
