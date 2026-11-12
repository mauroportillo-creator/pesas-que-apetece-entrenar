"""PVBPQAE-58 · Página de destino de cada pesa (Marta).

Es lo que se ve al escanear el QR de una pesa: qué pesa es y las opciones
para registrarse o iniciar sesión. También el aviso cuando el nivel de la
persona no encaja con el de la pesa.
"""
import streamlit as st

from comun import cuentas, datos, estilos
from comun.navegacion import ir_a


def entrar_a_rutina(pesa: dict | None) -> None:
    """Decide si mostrar el aviso de nivel o ir directamente a la pantalla principal.
    Sin pesa (se ha entrado sin QR) no hay aviso: se usa la pesa de su perfil."""
    usuario = cuentas.usuario_actual()
    st.session_state.seccion = "inicio"
    if pesa is None:
        ir_a("principal")
        return
    rutina = datos.obtener_rutina(pesa["rutina_id"])
    if usuario and usuario.get("nivel") and datos.comparar_nivel(usuario["nivel"], rutina["nivel"]) != 0:
        ir_a("aviso")
    else:
        ir_a("principal")


def mostrar(pesa: dict) -> None:
    rutina = datos.obtener_rutina(pesa["rutina_id"])
    estilos.tarjeta_pesa(pesa["peso_kg"], rutina["nivel"])

    usuario = cuentas.usuario_actual()
    if usuario and usuario.get("nivel"):
        estilos.titulo(f"¡Hola, {usuario['nombre']}! 👋",
                       "Todo listo para entrenar con esta pesa.")
        st.button("Entrar", type="primary", use_container_width=True,
                  on_click=entrar_a_rutina, args=(pesa,))
        st.button("Cerrar sesión", use_container_width=True, on_click=cuentas.cerrar_sesion)
        return

    estilos.titulo("Entrena con tu pesa",
                   "Crea tu cuenta para recibir una rutina adaptada a ti, "
                   "o inicia sesión si ya tienes una.")
    st.button("Registrarme", type="primary", use_container_width=True,
              on_click=ir_a, args=("registro",))
    st.button("Ya tengo cuenta · Iniciar sesión", use_container_width=True,
              on_click=ir_a, args=("login",))


def mostrar_aviso_nivel(pesa: dict) -> None:
    usuario = cuentas.usuario_actual()
    rutina = datos.obtener_rutina(pesa["rutina_id"])
    diferencia = datos.comparar_nivel(usuario["nivel"], rutina["nivel"])

    estilos.tarjeta_pesa(pesa["peso_kg"], rutina["nivel"])
    if diferencia > 0:
        estilos.titulo("Esta pesa puede quedarse corta ⚠️")
        st.warning(f"Por tus respuestas, tu nivel es **{usuario['nivel'].lower()}** y esta pesa "
                   f"está pensada para nivel **{rutina['nivel'].lower()}**. Puede que te resulte "
                   "demasiado fácil y no notes progreso.")
    else:
        estilos.titulo("Esta pesa puede ser exigente ⚠️")
        st.warning(f"Por tus respuestas, tu nivel es **{usuario['nivel'].lower()}** y esta pesa "
                   f"está pensada para nivel **{rutina['nivel'].lower()}**. Ve con calma y cuida "
                   "la técnica para evitar lesiones.")

    recomendadas = [p for p in datos.listar_pesas()
                    if datos.obtener_rutina(p["rutina_id"])["nivel"] == usuario["nivel"]]
    if recomendadas:
        pesos = " o ".join(f"{p['peso_kg']} kg" for p in recomendadas)
        st.info(f"Para tu nivel te recomendamos la pesa de **{pesos}**.")

    st.button("Continuar igualmente", type="primary", use_container_width=True,
              on_click=ir_a, args=("principal",))
    st.button("Volver", use_container_width=True, on_click=ir_a, args=("pesa",))
