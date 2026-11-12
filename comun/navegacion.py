"""Qué pantalla se está viendo y cómo pasar de una a otra."""
import streamlit as st


def pantalla_actual() -> str:
    return st.session_state.setdefault("pantalla", "pesa")


def ir_a(pantalla: str) -> None:
    st.session_state.pantalla = pantalla


def boton_volver(destino: str = "pesa", texto: str = "← Volver") -> None:
    st.button(texto, on_click=ir_a, args=(destino,), type="tertiary")
