"""PVBPQAE-46 · Perfil editable: «Mis datos» (Mauro)."""
import streamlit as st

from comun import cuentas, datos, estilos
from comun.navegacion import ir_a
from paginas.cuestionario import OBJETIVOS, empezar_de_nuevo


def mostrar() -> None:
    usuario = cuentas.usuario_actual()
    estilos.titulo("Mis datos", "Revisa y actualiza tu información.")

    with st.form("mis_datos"):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre", usuario["nombre"])
        apellidos = c2.text_input("Apellidos", usuario.get("apellidos", ""))
        st.text_input("Correo electrónico", usuario["correo"], disabled=True,
                      help="El correo no se puede cambiar desde aquí.")
        c3, c4 = st.columns(2)
        nivel = c3.selectbox("Nivel", datos.NIVELES,
                             index=datos.NIVELES.index(usuario["nivel"]) if usuario.get("nivel") else 0)
        objetivo = c4.selectbox("Objetivo", OBJETIVOS,
                                index=OBJETIVOS.index(usuario["objetivo"])
                                if usuario.get("objetivo") in OBJETIVOS else 0)
        guardar = st.form_submit_button("Guardar cambios", type="primary", use_container_width=True)

    if guardar:
        if not nombre.strip() or not apellidos.strip():
            st.error("El nombre y los apellidos no pueden quedar vacíos.")
        else:
            cuentas.actualizar_datos(nombre, apellidos, nivel, objetivo)
            st.success("Datos guardados.")

    st.write("")
    _, centro, _ = st.columns([1, 3, 1])
    with centro:
        st.markdown("<div style='text-align:center;opacity:.7;font-size:.9rem;margin-bottom:.4rem'>"
                    "¿Ha cambiado tu objetivo o has progresado?<br>Vuelve a hacer el cuestionario.</div>",
                    unsafe_allow_html=True)
        st.button("🔄 Repetir el cuestionario de nivel", key="repetir_cuestionario",
                  type="primary", use_container_width=True, on_click=_repetir_cuestionario)


def _repetir_cuestionario() -> None:
    empezar_de_nuevo()
    ir_a("cuestionario")
