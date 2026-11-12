"""PVBPQAE-46 · Gestión de usuarios (Mauro).

Registro (con código de confirmación por correo), inicio de sesión y
«¿Has olvidado tu contraseña?» (código por correo + contraseña nueva).
La conexión con Supabase Authentication está en comun/autenticacion.py.
"""
import streamlit as st

from comun import autenticacion, cuentas, estilos
from comun.navegacion import boton_volver, ir_a
from paginas.cuestionario import empezar_de_nuevo
from paginas.pesa import entrar_a_rutina

GENEROS = ["Mujer", "Hombre", "Otro", "Prefiero no decirlo"]


def _despues_de_entrar(pesa: dict) -> None:
    """Con nivel → a su rutina; sin nivel (cuenta nueva) → al cuestionario."""
    if cuentas.usuario_actual().get("nivel"):
        entrar_a_rutina(pesa)
    else:
        empezar_de_nuevo()
        ir_a("cuestionario")


# ---------------------------------------------------------------- registro
def mostrar_registro(pesa: dict) -> None:
    boton_volver()
    estilos.titulo("Crea tu cuenta", "Solo te llevará un minuto.")

    with st.form("registro", border=False):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre")
        apellidos = c2.text_input("Apellidos")
        c3, c4 = st.columns(2)
        edad = c3.number_input("Edad", min_value=16, max_value=99, value=None,
                               step=1, placeholder="Años")
        genero = c4.selectbox("Género", GENEROS, index=None, placeholder="Elige una opción")
        correo = st.text_input("Correo electrónico", placeholder="tu@correo.com")
        contrasena = st.text_input("Contraseña", type="password",
                                   help="Mínimo 8 caracteres.")
        repetir = st.text_input("Repite la contraseña", type="password")
        acepta = st.checkbox("Acepto la política de privacidad y el tratamiento de mis datos")
        enviar = st.form_submit_button("Crear cuenta", type="primary", use_container_width=True)

    if enviar:
        errores = []
        if not nombre.strip() or not apellidos.strip():
            errores.append("Escribe tu nombre y tus apellidos.")
        if edad is None:
            errores.append("Indica tu edad (mínimo 16 años).")
        if not genero:
            errores.append("Elige una opción en género.")
        if not autenticacion.correo_valido(correo):
            errores.append("El correo electrónico no es válido.")
        if len(contrasena) < 8:
            errores.append("La contraseña debe tener al menos 8 caracteres.")
        elif contrasena != repetir:
            errores.append("Las contraseñas no coinciden.")
        if not acepta:
            errores.append("Tienes que aceptar la política de privacidad.")

        if not errores:
            with st.spinner("Creando tu cuenta…"):
                estado, mensaje = autenticacion.registrar(nombre, apellidos, correo, contrasena,
                                                    edad=int(edad), genero=genero,
                                                    peso_pesa_kg=pesa["peso_kg"] if pesa else None)
            if estado == "error":
                errores.append(mensaje)
            elif estado == "confirmar":
                ir_a("confirmar")
                st.rerun()
            else:
                _despues_de_entrar(pesa)
                st.rerun()
        for e in errores:
            st.error(e)

    st.button("¿Ya tienes cuenta? Inicia sesión", type="tertiary",
              on_click=ir_a, args=("login",))


def mostrar_confirmar(pesa: dict) -> None:
    """Código de 6 dígitos que llega por correo al registrarse."""
    correo = st.session_state.get("correo_pendiente", "")
    boton_volver("login")
    estilos.titulo("Confirma tu correo 📩",
                   f"Te hemos enviado un código a **{correo}**. Escríbelo aquí para activar tu cuenta.")

    with st.form("confirmar", border=False):
        codigo = st.text_input("Código", max_chars=10, placeholder="Código del correo")
        enviar = st.form_submit_button("Confirmar", type="primary", use_container_width=True)

    if enviar:
        if not codigo.strip():
            st.error("Escribe el código que te hemos enviado.")
        else:
            error = autenticacion.confirmar_codigo(correo, codigo)
            if error:
                st.error(error)
            else:
                _despues_de_entrar(pesa)
                st.rerun()

    st.caption("¿No te ha llegado? Revisa la carpeta de spam.")
    if st.button("Reenviar código", type="tertiary"):
        error = autenticacion.reenviar_codigo(correo)
        st.error(error) if error else st.success("Te hemos enviado un código nuevo.")


# ---------------------------------------------------------------- inicio de sesión
def mostrar_login(pesa: dict) -> None:
    boton_volver()
    estilos.titulo("Inicia sesión", "Bienvenido/a de nuevo.")
    if st.session_state.pop("aviso_login", None):
        st.success("Contraseña cambiada. Ya puedes iniciar sesión con la nueva.")

    with st.form("login", border=False):
        correo = st.text_input("Correo electrónico", placeholder="tu@correo.com")
        contrasena = st.text_input("Contraseña", type="password")
        enviar = st.form_submit_button("Entrar", type="primary", use_container_width=True)

    if enviar:
        with st.spinner("Entrando…"):
            error = autenticacion.iniciar_sesion(correo, contrasena)
        if error:
            st.error(error)
            if "confirmado" in error:
                st.button("Introducir el código", on_click=ir_a, args=("confirmar",))
        else:
            _despues_de_entrar(pesa)
            st.rerun()

    st.button("¿Has olvidado tu contraseña?", type="tertiary",
              on_click=ir_a, args=("recuperar",))
    st.button("¿No tienes cuenta? Regístrate", type="tertiary",
              on_click=ir_a, args=("registro",))


# ---------------------------------------------------------------- recuperar contraseña
def _otro_correo() -> None:
    st.session_state.pop("correo_recuperar", None)


def mostrar_recuperar(pesa: dict) -> None:
    boton_volver("login")
    correo = st.session_state.get("correo_recuperar")

    if not correo:
        # Paso 1: pedir el correo
        estilos.titulo("¿Has olvidado tu contraseña?",
                       "Escribe tu correo y te enviaremos un código para crear una nueva.")
        with st.form("recuperar", border=False):
            correo_escrito = st.text_input("Correo electrónico", placeholder="tu@correo.com")
            enviar = st.form_submit_button("Enviar código", type="primary", use_container_width=True)
        if enviar:
            if not autenticacion.correo_valido(correo_escrito):
                st.error("El correo electrónico no es válido.")
            else:
                error = autenticacion.enviar_recuperacion(correo_escrito)
                if error:
                    st.error(error)
                else:
                    st.session_state.correo_recuperar = correo_escrito.strip().lower()
                    st.rerun()
        return

    # Paso 2: código + contraseña nueva
    estilos.titulo("Crea una contraseña nueva",
                   f"Si hay una cuenta con **{correo}**, te hemos enviado un código. "
                   "Revisa también la carpeta de spam.")
    with st.form("nueva_contrasena", border=False):
        codigo = st.text_input("Código", max_chars=10, placeholder="Código del correo")
        nueva = st.text_input("Contraseña nueva", type="password", help="Mínimo 8 caracteres.")
        repetir = st.text_input("Repite la contraseña nueva", type="password")
        guardar = st.form_submit_button("Guardar contraseña", type="primary", use_container_width=True)

    if guardar:
        if not codigo.strip():
            st.error("Escribe el código que te hemos enviado.")
        elif len(nueva) < 8:
            st.error("La contraseña debe tener al menos 8 caracteres.")
        elif nueva != repetir:
            st.error("Las contraseñas no coinciden.")
        else:
            error = autenticacion.cambiar_contrasena(correo, codigo, nueva)
            if error:
                st.error(error)
            else:
                st.session_state.pop("correo_recuperar", None)
                st.session_state.aviso_login = True
                ir_a("login")
                st.rerun()

    st.button("Usar otro correo", type="tertiary", on_click=_otro_correo)
