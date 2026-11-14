"""PVBPQAE-46 · Gestión de usuarios (Mauro): cuentas con Supabase Authentication.

Registro, código de confirmación, inicio de sesión y recuperar la contraseña.
- Supabase guarda el correo y la contraseña (cifrada) y envía los correos con un
  CÓDIGO: para confirmar la cuenta y para recuperar la contraseña.
- Al registrarse, el perfil se crea solo en la tabla «Registro de usuarios»
  (trigger en Supabase: 4_conectar_usuarios_con_cuentas.sql).

El cliente de Supabase y el perfil están en comun/cuentas.py.
"""
import re

import streamlit as st

from comun.cuentas import cargar_perfil, sb

PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Errores de Supabase traducidos al español
ERRORES = [
    ("invalid login credentials", "El correo o la contraseña no son correctos."),
    ("email not confirmed", "Todavía no has confirmado tu correo. Introduce el código que te enviamos."),
    ("rate limit", "Se han enviado demasiados correos seguidos. Espera unos minutos y vuelve a intentarlo."),
    ("security purposes", "Por seguridad, espera unos segundos antes de pedir otro código."),
    ("expired or is invalid", "El código no es correcto o ha caducado. Pide uno nuevo."),
    ("already registered", "Ya hay una cuenta con este correo. Prueba a iniciar sesión."),
    ("password should be", "La contraseña no es lo bastante segura (mínimo 8 caracteres)."),
    ("same password", "La contraseña nueva tiene que ser distinta de la anterior."),
    ("database error saving new user", "No se ha podido crear la cuenta. ¿Ya existe un usuario con este correo?"),
]


def _traducir(error: Exception) -> str:
    texto = str(error).lower()
    for clave, mensaje in ERRORES:
        if clave in texto:
            return mensaje
    return f"Ha ocurrido un error. Inténtalo de nuevo. ({error})"


def correo_valido(correo: str) -> bool:
    return bool(PATRON_CORREO.match(correo.strip()))


# ---------------------------------------------------------------- registro
def registrar(nombre: str, apellidos: str, correo: str, contrasena: str,
              edad: int, genero: str, peso_pesa_kg: int | None) -> tuple[str, str | None]:
    """Crea la cuenta. Devuelve ("ok" | "confirmar" | "error", mensaje)."""
    correo = correo.strip().lower()
    try:
        respuesta = sb().auth.sign_up({
            "email": correo,
            "password": contrasena,
            "options": {"data": {"nombre": nombre.strip(), "apellidos": apellidos.strip(),
                                 "edad": edad, "genero": genero, "peso_pesa_kg": peso_pesa_kg}},
        })
    except Exception as error:
        return "error", _traducir(error)

    # Si el correo ya existe, Supabase no da error pero devuelve el usuario sin identidades
    if respuesta.user and respuesta.user.identities == []:
        return "error", "Ya hay una cuenta con este correo. Prueba a iniciar sesión."
    if respuesta.session:  # «Confirm email» desactivado en Supabase
        cargar_perfil()
        return "ok", None
    st.session_state.correo_pendiente = correo
    return "confirmar", None


def confirmar_codigo(correo: str, codigo: str) -> str | None:
    """Confirma la cuenta con el código del correo. Devuelve un error o None."""
    try:
        sb().auth.verify_otp({"email": correo, "token": codigo.strip(), "type": "signup"})
    except Exception as error:
        return _traducir(error)
    cargar_perfil()
    return None


def reenviar_codigo(correo: str) -> str | None:
    try:
        sb().auth.resend({"type": "signup", "email": correo})
    except Exception as error:
        return _traducir(error)
    return None


# ---------------------------------------------------------------- inicio de sesión
def iniciar_sesion(correo: str, contrasena: str) -> str | None:
    """Comprueba correo y contraseña. Devuelve un mensaje de error o None."""
    try:
        sb().auth.sign_in_with_password({"email": correo.strip().lower(), "password": contrasena})
    except Exception as error:
        if "email not confirmed" in str(error).lower():
            st.session_state.correo_pendiente = correo.strip().lower()
        return _traducir(error)
    cargar_perfil()
    return None


# ---------------------------------------------------------------- recuperar contraseña
def enviar_recuperacion(correo: str) -> str | None:
    """Supabase envía un correo con un código para crear una contraseña nueva."""
    try:
        sb().auth.reset_password_for_email(correo.strip().lower())
    except Exception as error:
        return _traducir(error)
    return None


def cambiar_contrasena(correo: str, codigo: str, nueva: str) -> str | None:
    """Comprueba el código del correo y guarda la contraseña nueva."""
    try:
        sb().auth.verify_otp({"email": correo.strip().lower(), "token": codigo.strip(),
                              "type": "recovery"})
        sb().auth.update_user({"password": nueva})
        sb().auth.sign_out()
    except Exception as error:
        return _traducir(error)
    return None


# ---------------------------------------------------------------- eliminar la cuenta (RGPD)
def eliminar_cuenta() -> str | None:
    """Borra la cuenta, el perfil y las rutinas guardadas (PVBPQAE-56).

    Llama a la función eliminar_mi_cuenta de Supabase (6_eliminar_cuenta.sql),
    que solo puede borrar la cuenta de quien ha iniciado sesión. Devuelve un error o None.
    """
    try:
        sb().rpc("eliminar_mi_cuenta").execute()
    except Exception:
        return "No se ha podido eliminar la cuenta. Inténtalo de nuevo más tarde."
    st.session_state.pop("usuario", None)
    st.session_state.pop("sb", None)  # la sesión de Supabase ya no sirve
    return None
