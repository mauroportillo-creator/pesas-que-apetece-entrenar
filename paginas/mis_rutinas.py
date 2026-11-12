"""«Mis rutinas»: rutinas que la persona ha guardado (historia por asignar)."""
import streamlit as st

from comun import cuentas, datos, estilos
from paginas import rutina


def mostrar() -> None:
    usuario = cuentas.usuario_actual()
    estilos.titulo("Mis rutinas", "Las rutinas que has guardado para tenerlas a mano.")

    guardadas = [datos.rutina_por_id(i) for i in usuario.get("rutinas_guardadas", [])]
    guardadas = [r for r in guardadas if r]
    if not guardadas:
        st.info("Aún no has guardado ninguna rutina. En **Rutinas**, pulsa la estrella ☆ "
                "de las que más te gusten.")
        return
    for r in guardadas:
        rutina.desplegable(r, f"mia_{r['id']}")
