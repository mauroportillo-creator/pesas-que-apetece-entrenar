"""PVBPQAE-98 · Consejos de alimentación según mi objetivo (María; pantalla preparada con Marta).

Botón «🥗 Alimentación» de la barra de arriba (solo Premium; con el plan gratuito sale con
candado y lleva a «Hazte Premium», ver premium.py). De arriba abajo:
  1. Cabecera: «Tu objetivo: …» y botón «Cambiar objetivo» (lleva a «Mis datos»).
  2. Banner del objetivo: titular y subtítulo con su color.
  3. Aviso de salud completo (escenario 3).
  4. Los 5 consejos del objetivo (escenario 1).
  5. Menú de ejemplo: selector de día (L M X J V S D) y las 5 tomas del día con cantidades,
     kcal y macros, más el resumen del día.
  6. Aviso de salud corto.
El objetivo se lee cada vez que se abre la pantalla (escenario 2: si cambia en «Mis datos», se
ven los consejos del nuevo).

El contenido está en las tablas «alimentacion» y «menus_alimentacion»
(10_crear_tabla_alimentacion.sql). Se cambia en Supabase y, más adelante, desde el panel de
administración (PVBPQAE-95).
"""
from datetime import date

import streamlit as st

from comun import cuentas
from comun.navegacion import ir_a
from paginas.cuestionario import empezar_de_nuevo

AVISO_COMPLETO = (
    "**Recomendaciones generales.** Los consejos y menús de esta sección son recomendaciones "
    "generales de alimentación y no sustituyen el consejo de un profesional sanitario. Ante "
    "cualquier duda o problema de salud (por ejemplo, alergias o intolerancias, diabetes, embarazo "
    "o lactancia, enfermedades renales o cardiovasculares, o antecedentes de trastornos de la "
    "conducta alimentaria), consulta con tu médico o con un dietista-nutricionista antes de cambiar "
    "tu alimentación. Los menús contienen alérgenos como gluten, huevo, lácteos, pescado y frutos secos."
)
AVISO_CORTO = "Recomendaciones generales. Ante cualquier duda o problema de salud, consulta con un profesional."
DIAS = ["L", "M", "X", "J", "V", "S", "D"]
NOMBRES_DIA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


# ---------------------------------------------------------------- datos (Supabase)
def _contenido() -> dict | None:
    """Banners, consejos y menús de todos los objetivos (se leen una vez por sesión).
    Devuelve None si no se ha podido leer."""
    usuario = cuentas.usuario_actual()
    if "alimentacion" not in usuario:
        try:
            banners = cuentas.sb().table("alimentacion").select(
                "objetivo, titular, subtitulo, color, consejos").execute().data
            menus = (cuentas.sb().table("menus_alimentacion")
                     .select("objetivo, dia, orden, toma, plato, ingredientes, kcal, proteinas, hidratos, grasas")
                     .order("dia").order("orden").execute().data)
        except Exception:
            return None
        usuario["alimentacion"] = {
            "banners": {b["objetivo"].lower(): b for b in banners},
            "menus": menus,
        }
    return usuario["alimentacion"]


def _reintentar() -> None:
    cuentas.usuario_actual().pop("alimentacion", None)


def _cambiar_objetivo() -> None:
    st.session_state.seccion = "mis_datos"


def _hacer_cuestionario() -> None:
    empezar_de_nuevo()
    ir_a("cuestionario")


def _consejos(texto: str) -> list[tuple[str, str]]:
    """«Título | texto» por línea → [(título, texto)]."""
    lista = []
    for linea in (texto or "").splitlines():
        if linea.strip():
            titulo, _, explicacion = linea.partition("|")
            lista.append((titulo.strip(), explicacion.strip()))
    return lista


# ---------------------------------------------------------------- bloques de la pantalla
def _banner(objetivo: str, banner: dict) -> None:
    color = banner.get("color") or "#C2410C"
    st.markdown(
        f'<div style="background:{color};color:#fff;border-radius:18px;padding:1.2rem 1.2rem 1.3rem;'
        f'margin:.4rem 0 1rem">'
        f'<div style="font-size:.75rem;letter-spacing:.1em;font-weight:700;opacity:.85">'
        f'OBJETIVO · {objetivo.upper()}</div>'
        f'<div style="font-size:1.35rem;font-weight:800;line-height:1.25;margin:.35rem 0">'
        f'{banner.get("titular") or ""}</div>'
        f'<div style="opacity:.92">{banner.get("subtitulo") or ""}</div></div>',
        unsafe_allow_html=True,
    )


def _lista_consejos(banner: dict) -> None:
    st.subheader("Consejos para tu objetivo")
    for n, (titulo, texto) in enumerate(_consejos(banner.get("consejos")), start=1):
        with st.container(border=True):
            st.markdown(f"**{n}. {titulo}**  \n{texto}")


def _menu(objetivo: str, menus: list[dict]) -> None:
    st.subheader("Menú de ejemplo")
    del_objetivo = [m for m in menus if m["objetivo"].lower() == objetivo.lower()]
    if not del_objetivo:
        st.info("Estamos preparando el menú de tu objetivo. ¡Muy pronto!")
        return
    hoy = DIAS[date.today().weekday()]
    elegido = st.pills("Día", DIAS, default=hoy, key="alimentacion_dia", label_visibility="collapsed") or hoy
    numero = DIAS.index(elegido) + 1
    tomas = sorted((m for m in del_objetivo if m["dia"] == numero), key=lambda m: m["orden"])
    st.caption(f"{NOMBRES_DIA[numero - 1]} · {len(tomas)} tomas")

    for t in tomas:
        with st.container(border=True):
            st.markdown(f"**{t['toma']}** · {t['plato']}")
            if t.get("ingredientes"):
                st.markdown("\n".join(f"- {i.strip()}" for i in t["ingredientes"].split(";") if i.strip()))
            st.caption(f"🔥 {t['kcal']} kcal · Proteínas {t['proteinas']} g · "
                       f"Hidratos {t['hidratos']} g · Grasas {t['grasas']} g")

    if tomas:
        st.markdown("**Resumen del día**")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Kcal", sum(t["kcal"] or 0 for t in tomas), border=True)
        c2.metric("Proteínas", f"{sum(t['proteinas'] or 0 for t in tomas)} g", border=True)
        c3.metric("Hidratos", f"{sum(t['hidratos'] or 0 for t in tomas)} g", border=True)
        c4.metric("Grasas", f"{sum(t['grasas'] or 0 for t in tomas)} g", border=True)


# ---------------------------------------------------------------- pantalla
def mostrar() -> None:
    objetivo = cuentas.usuario_actual().get("objetivo")  # se lee cada vez (escenario 2)

    # 1. Cabecera
    st.markdown('<div class="titulo">Alimentación 🥗</div>', unsafe_allow_html=True)
    if objetivo:
        izquierda, derecha = st.columns([3, 2], vertical_alignment="center")
        izquierda.markdown(f"Tu objetivo: **{objetivo}**")
        derecha.button("Cambiar objetivo", key="alimentacion_cambiar", type="tertiary",
                       on_click=_cambiar_objetivo)

    if not objetivo:
        st.info("Completa el cuestionario para ver consejos de alimentación para tu objetivo.")
        st.button("Hacer el cuestionario", type="primary", on_click=_hacer_cuestionario)
        st.info(f"ℹ️ {AVISO_COMPLETO}")
        return

    contenido = _contenido()
    if contenido is None:
        st.error("No hemos podido cargar los consejos de alimentación.")
        st.button("Reintentar", on_click=_reintentar)
        st.info(f"ℹ️ {AVISO_COMPLETO}")
        return

    banner = contenido["banners"].get(objetivo.lower())
    if banner and banner.get("titular"):
        _banner(objetivo, banner)                       # 2. Banner
    st.info(f"ℹ️ {AVISO_COMPLETO}")                     # 3. Aviso completo
    if banner and banner.get("consejos"):
        _lista_consejos(banner)                         # 4. Consejos
    else:
        st.info("Estamos preparando los consejos para tu objetivo. ¡Muy pronto!")
    _menu(objetivo, contenido["menus"])                 # 5. Menú de ejemplo
    st.caption(f"ℹ️ {AVISO_CORTO}")                     # 6. Aviso corto
