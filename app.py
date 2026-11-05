"""App Streamlit: menú lateral (Usuario, Mis Datos, Mis Rutinas) y
botones superiores (Inicio, Rutinas, Tienda).

Ejecutar con:  streamlit run app.py
"""
import json
from pathlib import Path

import streamlit as st

BASE = Path(__file__).parent
DATOS = BASE / "datos.json"
INICIO = BASE / "inicio.md"

st.set_page_config(page_title="Mi App de Entrenamiento", page_icon="💪", layout="wide")


# ---------- Datos ----------
def cargar_datos() -> dict:
    return json.loads(DATOS.read_text(encoding="utf-8"))


def guardar_datos(datos: dict) -> None:
    DATOS.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


datos = cargar_datos()
usuario = datos["usuario"]

if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"
if "carrito" not in st.session_state:
    st.session_state.carrito = {}


def ir_a(pagina: str) -> None:
    st.session_state.pagina = pagina


# ---------- Estilos ----------
st.markdown(
    """
    <style>
    .avatar {width:64px;height:64px;border-radius:50%;background:#4f8bf9;color:#fff;
             display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:700;}
    .nombre-usuario {font-size:1.1rem;font-weight:700;margin:0;}
    .email-usuario {font-size:0.8rem;opacity:0.7;margin:0;}
    .tarjeta {border:1px solid rgba(128,128,128,.3);border-radius:12px;padding:1rem;height:100%;}
    .icono-producto {font-size:3rem;text-align:center;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Barra lateral ----------
with st.sidebar:
    # 1) Usuario con foto de perfil a la izquierda
    col_foto, col_nombre = st.columns([1, 2], vertical_alignment="center")
    with col_foto:
        foto = BASE / usuario.get("foto", "")
        if usuario.get("foto") and foto.is_file():
            st.image(str(foto), width=64)
        else:
            iniciales = "".join(p[0] for p in usuario["nombre"].split()[:2]).upper()
            st.markdown(f'<div class="avatar">{iniciales}</div>', unsafe_allow_html=True)
    with col_nombre:
        st.markdown(
            f'<p class="nombre-usuario">{usuario["nombre"]}</p>'
            f'<p class="email-usuario">{usuario["email"]}</p>',
            unsafe_allow_html=True,
        )
    st.button("👤 Usuario", use_container_width=True, on_click=ir_a, args=("Usuario",))

    st.divider()
    # 2) Mis Datos   3) Mis Rutinas
    st.button("📋 Mis Datos", use_container_width=True, on_click=ir_a, args=("Mis Datos",))
    st.button("🗓️ Mis Rutinas", use_container_width=True, on_click=ir_a, args=("Mis Rutinas",))

    if st.session_state.carrito:
        st.divider()
        n = sum(st.session_state.carrito.values())
        st.button(f"🛒 Carrito ({n})", use_container_width=True, on_click=ir_a, args=("Tienda",))


# ---------- Botones superiores centrados ----------
_, c1, c2, c3, _ = st.columns([2, 1, 1, 1, 2])
for col, nombre, icono in [(c1, "Inicio", "🏠"), (c2, "Rutinas", "💪"), (c3, "Tienda", "🛍️")]:
    with col:
        st.button(
            f"{icono} {nombre}",
            use_container_width=True,
            type="primary" if st.session_state.pagina == nombre else "secondary",
            on_click=ir_a,
            args=(nombre,),
        )
st.divider()


# ---------- Páginas ----------
def pagina_inicio():
    st.title("🏠 Inicio")
    texto = INICIO.read_text(encoding="utf-8") if INICIO.exists() else ""
    st.markdown(texto)

    with st.expander("✏️ Editar descripción"):
        nuevo = st.text_area("Texto (admite Markdown)", value=texto, height=200)
        if st.button("Guardar descripción"):
            INICIO.write_text(nuevo, encoding="utf-8")
            st.success("Descripción guardada.")
            st.rerun()


def tarjeta_rutina(r: dict, clave: str, mostrar_añadir=True, mostrar_quitar=False):
    with st.container(border=True):
        st.subheader(r["nombre"])
        st.caption(f'Nivel: {r["nivel"]} · {r["duracion_min"]} min · {r["dias_semana"]} días/semana')
        st.write(r["descripcion"])
        with st.expander("Ver ejercicios"):
            for e in r["ejercicios"]:
                st.markdown(f"- {e}")
        if mostrar_añadir:
            if r["nombre"] in datos["mis_rutinas"]:
                st.button("✅ En Mis Rutinas", key=f"en_{clave}", disabled=True)
            elif st.button("➕ Añadir a Mis Rutinas", key=f"add_{clave}"):
                datos["mis_rutinas"].append(r["nombre"])
                guardar_datos(datos)
                st.rerun()
        if mostrar_quitar and st.button("🗑️ Quitar", key=f"del_{clave}"):
            datos["mis_rutinas"].remove(r["nombre"])
            guardar_datos(datos)
            st.rerun()


def pagina_rutinas():
    st.title("💪 Rutinas")
    niveles = sorted({r["nivel"] for r in datos["rutinas"]})
    filtro = st.multiselect("Filtrar por nivel", niveles)
    rutinas = [r for r in datos["rutinas"] if not filtro or r["nivel"] in filtro]
    cols = st.columns(2)
    for i, r in enumerate(rutinas):
        with cols[i % 2]:
            tarjeta_rutina(r, f"rut_{i}")


def pagina_tienda():
    st.title("🛍️ Tienda")
    productos = datos["productos"]
    categorias = ["Todas"] + sorted({p["categoria"] for p in productos})
    cat = st.radio("Categoría", categorias, horizontal=True)
    visibles = [p for p in productos if cat == "Todas" or p["categoria"] == cat]

    cols = st.columns(3)
    for i, p in enumerate(visibles):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f'<div class="icono-producto">{p["icono"]}</div>', unsafe_allow_html=True)
                st.markdown(f'**{p["nombre"]}**')
                st.caption(p["categoria"])
                st.markdown(f'### {p["precio"]:.2f} €')
                cant = st.number_input("Cantidad", 1, 20, 1, key=f"cant_{p['nombre']}")
                if st.button("🛒 Añadir al carrito", key=f"buy_{p['nombre']}", use_container_width=True):
                    st.session_state.carrito[p["nombre"]] = st.session_state.carrito.get(p["nombre"], 0) + cant
                    st.toast(f'{cant} × {p["nombre"]} añadido al carrito')
                    st.rerun()

    st.divider()
    st.subheader("🛒 Carrito")
    if not st.session_state.carrito:
        st.info("El carrito está vacío.")
        return
    precios = {p["nombre"]: p["precio"] for p in productos}
    total = 0.0
    for nombre, cant in list(st.session_state.carrito.items()):
        subtotal = precios[nombre] * cant
        total += subtotal
        a, b, c = st.columns([4, 2, 1])
        a.write(f"{cant} × {nombre}")
        b.write(f"{subtotal:.2f} €")
        if c.button("❌", key=f"quitar_{nombre}"):
            del st.session_state.carrito[nombre]
            st.rerun()
    st.markdown(f"**Total: {total:.2f} €**")
    if st.button("Finalizar compra", type="primary"):
        st.session_state.carrito = {}
        st.success("¡Compra realizada! (simulación, no se ha cobrado nada)")
        st.balloons()


def pagina_usuario():
    st.title("👤 Usuario")
    col_foto, col_info = st.columns([1, 4], vertical_alignment="center")
    with col_foto:
        foto = BASE / usuario.get("foto", "")
        if usuario.get("foto") and foto.is_file():
            st.image(str(foto), width=120)
        else:
            iniciales = "".join(p[0] for p in usuario["nombre"].split()[:2]).upper()
            st.markdown(
                f'<div class="avatar" style="width:120px;height:120px;font-size:48px">{iniciales}</div>',
                unsafe_allow_html=True,
            )
    with col_info:
        st.subheader(usuario["nombre"])
        st.write(usuario["email"])
        st.write(f'Objetivo: **{usuario["objetivo"]}** · Rutinas guardadas: **{len(datos["mis_rutinas"])}**')

    subida = st.file_uploader("Cambiar foto de perfil", type=["png", "jpg", "jpeg"])
    if subida is not None and st.session_state.get("foto_subida") != subida.file_id:
        st.session_state.foto_subida = subida.file_id
        destino = BASE / "assets" / f"perfil{Path(subida.name).suffix.lower()}"
        destino.parent.mkdir(exist_ok=True)
        destino.write_bytes(subida.getvalue())
        usuario["foto"] = destino.relative_to(BASE).as_posix()
        guardar_datos(datos)
        st.success("Foto actualizada.")
        st.rerun()


def pagina_mis_datos():
    st.title("📋 Mis Datos")
    with st.form("form_datos"):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre", usuario["nombre"])
        email = c2.text_input("Email", usuario["email"])
        edad = c1.number_input("Edad", 0, 120, int(usuario["edad"]))
        objetivos = ["Ganar fuerza", "Perder peso", "Ganar masa muscular", "Mejorar resistencia", "Salud general"]
        actual = objetivos.index(usuario["objetivo"]) if usuario["objetivo"] in objetivos else 0
        objetivo = c2.selectbox("Objetivo", objetivos, index=actual)
        peso = c1.number_input("Peso (kg)", 0.0, 300.0, float(usuario["peso_kg"]), step=0.5)
        altura = c2.number_input("Altura (cm)", 0, 250, int(usuario["altura_cm"]))
        if st.form_submit_button("Guardar", type="primary"):
            usuario.update(nombre=nombre, email=email, edad=edad, objetivo=objetivo, peso_kg=peso, altura_cm=altura)
            guardar_datos(datos)
            st.success("Datos guardados.")
            st.rerun()

    if usuario["altura_cm"]:
        imc = usuario["peso_kg"] / (usuario["altura_cm"] / 100) ** 2
        st.metric("IMC", f"{imc:.1f}")


def pagina_mis_rutinas():
    st.title("🗓️ Mis Rutinas")
    mias = [r for r in datos["rutinas"] if r["nombre"] in datos["mis_rutinas"]]
    if not mias:
        st.info("Aún no tienes rutinas guardadas.")
        st.button("Ver rutinas disponibles", on_click=ir_a, args=("Rutinas",))
        return
    cols = st.columns(2)
    for i, r in enumerate(mias):
        with cols[i % 2]:
            tarjeta_rutina(r, f"mia_{i}", mostrar_añadir=False, mostrar_quitar=True)


PAGINAS = {
    "Inicio": pagina_inicio,
    "Rutinas": pagina_rutinas,
    "Tienda": pagina_tienda,
    "Usuario": pagina_usuario,
    "Mis Datos": pagina_mis_datos,
    "Mis Rutinas": pagina_mis_rutinas,
}
PAGINAS[st.session_state.pagina]()
