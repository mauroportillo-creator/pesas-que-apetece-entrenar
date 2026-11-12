"""PVBPQAE-46 · Gestión de usuarios (Mauro).

PROVISIONAL: este archivo lo sustituye Mauro con su versión (registro con código
de confirmación, inicio de sesión y «¿Has olvidado tu contraseña?").
Mantiene los mismos nombres de funciones para que la web funcione mientras tanto.
"""
import streamlit as st

from comun import estilos
from comun.navegacion import boton_volver


def _proximamente(titulo: str) -> None:
    boton_volver()
    estilos.titulo(titulo)
    st.info("🛠️ Próximamente. Esta parte la está preparando el equipo (historia PVBPQAE-46).")


def mostrar_registro(pesa: dict | None) -> None:
    _proximamente("Crea tu cuenta")


def mostrar_confirmar(pesa: dict | None) -> None:
    _proximamente("Confirma tu correo")


def mostrar_login(pesa: dict | None) -> None:
    _proximamente("Inicia sesión")


def mostrar_recuperar(pesa: dict | None) -> None:
    _proximamente("¿Has olvidado tu contraseña?")
