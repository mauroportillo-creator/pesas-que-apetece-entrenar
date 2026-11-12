"""PVBPQAE-58 · Página general de inicio (Marta).

Es lo que se ve al abrir la web SIN escanear ningún QR: qué es la app y
el acceso a registro e inicio de sesión (escenario 2 de la historia).
"""
import streamlit as st

from comun import cuentas, datos, estilos
from comun.navegacion import ir_a
from paginas.pesa import entrar_a_rutina

VENTAJAS = [
    ("📱", "Escanea el QR de tu pesa", "Se abre la web al momento, sin descargar nada."),
    ("🎯", "Una rutina para ti", "Adaptada a tu nivel y a tu objetivo."),
    ("⭐", "Guarda tus favoritas", "Tenlas siempre a mano en «Mis rutinas»."),
]


def _simular_escaneo(codigo: str) -> None:
    st.query_params["pesa"] = codigo
    ir_a("pesa")


def mostrar(_pesa=None) -> None:
    st.markdown(
        '<div class="portada">'
        '<div class="portada-titulo">Entrena con tu pesa, sin descargar nada</div>'
        '<div class="portada-texto">Rutinas de fuerza guiadas y adaptadas a tu nivel, '
        'directamente desde el móvil.</div></div>',
        unsafe_allow_html=True,
    )

    usuario = cuentas.usuario_actual()
    if usuario and usuario.get("nivel"):
        estilos.titulo(f"¡Hola de nuevo, {usuario['nombre']}! 👋")
        st.button("Entrar", type="primary", use_container_width=True,
                  on_click=entrar_a_rutina, args=(None,))
        st.button("Cerrar sesión", use_container_width=True, on_click=cuentas.cerrar_sesion)
    else:
        st.button("Registrarme", type="primary", use_container_width=True,
                  on_click=ir_a, args=("registro",))
        st.button("Ya tengo cuenta · Iniciar sesión", use_container_width=True,
                  on_click=ir_a, args=("login",))

    st.write("")
    for icono, titulo, texto in VENTAJAS:
        st.markdown(
            f'<div class="ventaja"><div class="ventaja-icono">{icono}</div>'
            f'<div><div class="ventaja-titulo">{titulo}</div>'
            f'<div class="ventaja-texto">{texto}</div></div></div>',
            unsafe_allow_html=True,
        )

    # Solo para probar mientras no haya QR impresos
    with st.expander("🧪 Probar sin QR: simular que escaneo una pesa"):
        for p in datos.listar_pesas():
            st.button(f"Pesa de {p['peso_kg']} kg", use_container_width=True,
                      on_click=_simular_escaneo, args=(p["codigo"],), key=f"sim_{p['codigo']}")
