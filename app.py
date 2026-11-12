"""Pesas que apetece enseñar · Web (Streamlit)

Arrancar:  python -m streamlit run app.py

Cada pesa tiene un QR con una dirección del tipo  .../?pesa=<código>
Sin QR se abre la página general de inicio, con acceso a registro e inicio de sesión;
al entrar se usa la pesa del perfil de la persona.

Cada pantalla está en su propio archivo dentro de  paginas/  (uno por historia):
  inicio.py          PVBPQAE-58  Página general de inicio (sin QR)      (Marta)
  pesa.py            PVBPQAE-58  Página de cada pesa y aviso de nivel   (Marta)
  registro_login.py  PVBPQAE-46  Registro, inicio de sesión, recuperar  (Mauro)
  cuestionario.py    PVBPQAE-27  Cuestionario de nivel y objetivo       (María Luz)
  principal.py       PVBPQAE-58  Pantalla principal: panel y barra      (Marta)
  rutina.py          PVBPQAE-25  Cómo se muestra una rutina             (María Luz)
  mis_datos.py       PVBPQAE-46  Mis datos (perfil editable)            (Mauro)
  mis_rutinas.py     por asignar Rutinas guardadas
  tienda.py          por asignar Tienda de pesas
"""
import streamlit as st

from comun import cuentas, datos, estilos
from comun.navegacion import ir_a, pantalla_actual
from paginas import cuestionario, inicio, pesa, principal, registro_login

st.set_page_config(page_title="Pesas que apetece enseñar", page_icon="🏋️", layout="centered")


def ir_a_la_portada() -> None:
    st.query_params.clear()
    ir_a("pesa")


codigo = st.query_params.get("pesa")
pesa_actual = datos.obtener_pesa(codigo)

# Si se escanea otra pesa (o se entra sin QR), se vuelve a la página de inicio
if st.session_state.get("codigo_pesa") != codigo:
    st.session_state.codigo_pesa = codigo
    ir_a("pesa")

usuario = cuentas.usuario_actual()
en_principal = pantalla_actual() == "principal" and bool(usuario)
estilos.aplicar(con_panel=en_principal)
if not en_principal:  # la pantalla principal pinta su propia cabecera, con el carrito
    estilos.cabecera()

if codigo and not pesa_actual:
    estilos.titulo("No encontramos esta pesa 🤔",
                   "El código del QR no es válido. Prueba a escanearlo de nuevo.")
    st.button("Ir a la página de inicio", type="primary", on_click=ir_a_la_portada)
    st.stop()

# Sin QR, en la pantalla principal se usa la pesa del perfil de la persona
if en_principal and not pesa_actual:
    pesa_actual = datos.pesa_para_usuario(usuario)

PANTALLAS = {
    "pesa": pesa.mostrar if pesa_actual else inicio.mostrar,
    "aviso": pesa.mostrar_aviso_nivel,
    "registro": registro_login.mostrar_registro,
    "confirmar": registro_login.mostrar_confirmar,
    "login": registro_login.mostrar_login,
    "recuperar": registro_login.mostrar_recuperar,
    "cuestionario": cuestionario.mostrar,
    "principal": principal.mostrar,
}
PANTALLAS.get(pantalla_actual(), PANTALLAS["pesa"])(pesa_actual)
