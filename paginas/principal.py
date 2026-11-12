"""PVBPQAE-58 · Pantalla principal (Marta).

Panel lateral (usuario, Mis datos, Mis rutinas) y barra superior
(Inicio, Rutinas, Tienda). Cada sección está en su propio archivo.
"""
import streamlit as st

from comun import cuentas, datos, estilos
from comun.navegacion import ir_a
from paginas import carrito, mis_datos, mis_rutinas, rutina, tienda

BARRA = [("inicio", "🏠 Inicio"), ("rutinas", "💪 Rutinas"), ("tienda", "🛍️ Tienda")]


def ir_a_seccion(seccion: str) -> None:
    st.session_state.seccion = seccion


def salir() -> None:
    cuentas.cerrar_sesion()
    st.session_state.seccion = "inicio"
    ir_a("pesa")


def panel_lateral(usuario: dict, seccion: str) -> None:
    with st.sidebar:
        st.markdown(
            f'<div class="usuario"><div class="avatar">'
            f'{estilos.iniciales(usuario["nombre"], usuario.get("apellidos", ""))}</div>'
            f'<div><div class="nombre">{usuario["nombre"]} {usuario.get("apellidos", "")}</div>'
            f'<div class="correo">{usuario["correo"]}</div>'
            f'<span class="chip">Nivel {(usuario.get("nivel") or "—").lower()}</span></div></div>',
            unsafe_allow_html=True,
        )
        for clave, texto in [("mis_datos", "👤 Mis datos"), ("mis_rutinas", "⭐ Mis rutinas")]:
            st.button(texto, key=f"lat_{clave}", use_container_width=True,
                      type="primary" if seccion == clave else "secondary",
                      on_click=ir_a_seccion, args=(clave,))
        st.divider()
        st.button("Cerrar sesión", key="lat_salir", use_container_width=True, type="tertiary",
                  on_click=salir)


def cabecera_con_carrito(seccion: str) -> None:
    """Marca a la izquierda y carrito a la derecha, con el número de productos encima."""
    izquierda, derecha = st.columns([5, 1], vertical_alignment="center")
    with izquierda:
        estilos.cabecera()
    with derecha:
        st.button("🛒", key="icono_carrito", help="Ver carrito",
                  type="primary" if seccion == "carrito" else "secondary",
                  on_click=ir_a_seccion, args=("carrito",))
    unidades = carrito.total_unidades()
    if unidades:
        estilos.contador_carrito(unidades)


def barra_superior(seccion: str) -> None:
    columnas = st.columns(len(BARRA))
    for col, (clave, texto) in zip(columnas, BARRA):
        col.button(texto, key=f"barra_{clave}", use_container_width=True,
                   type="primary" if seccion == clave else "secondary",
                   on_click=ir_a_seccion, args=(clave,))
    st.write("")


def rutina_de_hoy(pesa: dict, usuario: dict) -> dict:
    """La rutina de la pesa escaneada para su objetivo; si no hay, la principal de la pesa."""
    return (datos.rutina_de_objetivo(pesa["peso_kg"], usuario.get("objetivo"))
            or datos.rutina_por_id(pesa["rutina_id"]))


def inicio(pesa: dict, usuario: dict) -> None:
    recomendada = rutina_de_hoy(pesa, usuario)
    objetivo = (usuario.get("objetivo") or "").lower()
    estilos.titulo(f"¡Hola, {usuario['nombre']}! 👋",
                   f"Esta es la rutina de tu pesa para tu objetivo: {objetivo}." if objetivo
                   else "Esta es la rutina de la pesa que has escaneado.")
    escaneada = bool(st.query_params.get("pesa"))
    estilos.tarjeta_pesa(pesa["peso_kg"], recomendada["nivel"],
                         "Has escaneado tu pesa" if escaneada else "Tu pesa")
    st.subheader("Tu rutina de hoy")
    rutina.desplegable(recomendada, "inicio", abierta=True)
    st.button("Ver todas las rutinas de esta pesa →", type="tertiary",
              on_click=ir_a_seccion, args=("rutinas",))


def rutinas(pesa: dict, usuario: dict) -> None:
    nivel = usuario.get("nivel") or "Principiante"
    de_la_pesa = datos.rutinas_de_pesa(pesa["peso_kg"])
    nivel_pesa = de_la_pesa[0]["nivel"] if de_la_pesa else nivel
    estilos.titulo("Rutinas", f"Las rutinas de tu pesa de {pesa['peso_kg']} kg, "
                              f"una para cada objetivo (nivel {nivel_pesa.lower()}).")

    # Primero la de su objetivo, luego el resto
    recomendada = rutina_de_hoy(pesa, usuario)
    for r in sorted(de_la_pesa, key=lambda r: r["id"] != recomendada["id"]):
        if r["id"] == recomendada["id"]:
            st.caption("🎯 Para tu objetivo")
        rutina.desplegable(r, f"rut_{r['id']}")
    if not de_la_pesa:
        st.info("Todavía no hay rutinas para esta pesa. ¡Muy pronto!")

    # Si la pesa no es de su nivel, también ve las de su nivel (sin repetir: 3 y 5 kg comparten)
    if nivel_pesa != nivel:
        vistas, de_mi_nivel = set(), []
        for r in datos.rutinas_de_nivel(nivel):
            if r["nombre"] not in vistas:
                vistas.add(r["nombre"])
                de_mi_nivel.append(r)
        if de_mi_nivel:
            pesas = " o ".join(f"{p['peso_kg']} kg" for p in datos.listar_pesas()
                               if datos.obtener_rutina(p["rutina_id"])["nivel"] == nivel)
            st.subheader(f"Para tu nivel ({nivel.lower()})")
            st.caption(f"Con la pesa de {pesas}.")
            for r in de_mi_nivel:
                rutina.desplegable(r, f"nivel_{r['id']}")


def mostrar(pesa: dict) -> None:
    usuario = cuentas.usuario_actual()
    if not usuario:
        ir_a("pesa")
        st.rerun()

    seccion = st.session_state.setdefault("seccion", "inicio")
    panel_lateral(usuario, seccion)
    cabecera_con_carrito(seccion)
    barra_superior(seccion)

    if seccion == "rutinas":
        rutinas(pesa, usuario)
    elif seccion == "tienda":
        tienda.mostrar(ir_a_seccion)
    elif seccion == "carrito":
        carrito.mostrar(ir_a_seccion)
    elif seccion == "mis_datos":
        mis_datos.mostrar()
    elif seccion == "mis_rutinas":
        mis_rutinas.mostrar()
    else:
        inicio(pesa, usuario)
