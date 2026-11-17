"""PVBPQAE-31 · Resumen y valoración al terminar la rutina (Javier).

1. «▶️ Empezar rutina» (en cada rutina) abre la pantalla de entrenar: se marcan las series hechas.
2. «🏁 Finalizar rutina» muestra el resumen: ejercicios completados, series y duración total.
   Se puede finalizar sin hacer todas las series: el resumen sale como «parcial».
3. La persona valora el esfuerzo (Fácil, Adecuada o Dura) o lo salta.
   La valoración se guarda en Supabase y ajusta la siguiente rutina:
   fácil sube, adecuada mantiene, dura mantiene (y si es dura dos veces seguidas, baja).

Cada sesión se guarda en la tabla «sesiones_entrenamiento» (7_crear_tabla_sesiones.sql),
donde cada persona solo ve las suyas (RLS). Si esa tabla todavía no existe en Supabase,
el resumen y la valoración funcionan igual, pero solo mientras la sesión está abierta.
"""
import re
from datetime import datetime, timezone

import streamlit as st

from comun import cuentas, datos, estilos

TABLA = "sesiones_entrenamiento"
VALORACIONES = [("Fácil", "😌 Fácil"), ("Adecuada", "👍 Adecuada"), ("Dura", "😮‍💨 Dura")]


# ---------------------------------------------------------------- ejercicios y series
def series_de(ejercicio: str, descripcion: str = "") -> int:
    """Series de un ejercicio: «Sentadilla 3x12» son 3. Si no lo pone, las rondas
    de la rutina («Se hace en 4 rondas») y, si tampoco, 1."""
    series = re.search(r"(\d+)\s*x\s*\d+", ejercicio)
    if series:
        return int(series.group(1))
    rondas = re.search(r"en (\d+) rondas", descripcion or "")
    return int(rondas.group(1)) if rondas else 1


def ejercicios_de(rutina: dict) -> list[tuple[str, int]]:
    """Lista de (ejercicio, número de series) de una rutina."""
    nombres = [e.strip() for e in (rutina.get("ejercicios") or "").split(";") if e.strip()]
    return [(n, series_de(n, rutina.get("descripcion"))) for n in nombres]


def calcular_resumen(ejercicios: list[tuple[str, int]], hechas: list[int],
                     inicio: datetime, fin: datetime) -> dict:
    """Resumen de la sesión. `hechas` son las series marcadas de cada ejercicio."""
    hechas = [min(h, s) for h, (_, s) in zip(hechas, ejercicios)]
    series_total = sum(s for _, s in ejercicios)
    series_hechas = sum(hechas)
    return {
        "ejercicios_completados": sum(1 for h, (_, s) in zip(hechas, ejercicios) if h >= s),
        "ejercicios_total": len(ejercicios),
        "series_hechas": series_hechas,
        "series_total": series_total,
        "duracion_min": max(1, round((fin - inicio).total_seconds() / 60)),
        "estado": "Completa" if series_hechas == series_total else "Parcial",
    }


# ---------------------------------------------------------------- regla de ajuste
def regla_de_ajuste(valoraciones: list[str]) -> str | None:
    """«sube», «mantiene» o «baja» según las valoraciones (la más reciente, la última).
    Fácil sube, adecuada mantiene, dura mantiene; dura dos veces seguidas, baja."""
    if not valoraciones:
        return None
    ultima = valoraciones[-1]
    if ultima == "Fácil":
        return "sube"
    if ultima == "Dura" and valoraciones[-2:] == ["Dura", "Dura"]:
        return "baja"
    return "mantiene"


def recomendacion(pesa: dict, valoraciones: list[str]) -> str | None:
    """Texto para la siguiente rutina según la regla de ajuste."""
    ajuste = regla_de_ajuste(valoraciones)
    if ajuste is None:
        return None
    pesos = [p["peso_kg"] for p in datos.listar_pesas()]
    mas = [p for p in pesos if p > pesa["peso_kg"]]
    menos = [p for p in pesos if p < pesa["peso_kg"]]
    if ajuste == "sube":
        return ("💪 La última rutina te resultó **fácil**: toca subir. "
                + (f"Prueba con la pesa de **{mas[0]} kg** o añade una serie a cada ejercicio."
                   if mas else "Añade una serie a cada ejercicio."))
    if ajuste == "baja":
        return ("🧘 Las dos últimas rutinas te resultaron **duras**: vamos a bajar un poco. "
                + (f"Prueba con la pesa de **{menos[-1]} kg** o haz una serie menos de cada ejercicio."
                   if menos else "Haz una serie menos de cada ejercicio."))
    if valoraciones[-1] == "Dura":
        return ("👌 La última rutina te resultó **dura**: mantenemos la misma. "
                "Ve con calma y cuida la técnica.")
    return "👍 La última rutina te resultó **adecuada**: seguimos con la misma."


# ---------------------------------------------------------------- Supabase
def _falta_la_tabla(error: Exception) -> bool:
    texto = str(error).lower()
    return "pgrst205" in texto or "42p01" in texto or "could not find the table" in texto


def valoraciones_recientes() -> list[str]:
    """Últimas valoraciones de la persona (de la más antigua a la más reciente)."""
    usuario = cuentas.usuario_actual()
    if "valoraciones" not in usuario:
        try:
            filas = (cuentas.sb().table(TABLA).select("valoracion")
                     .not_.is_("valoracion", "null").order("fin", desc=True).limit(2)
                     .execute().data)
            usuario["valoraciones"] = [f["valoracion"] for f in reversed(filas)]
        except Exception:
            usuario["valoraciones"] = []
    return usuario["valoraciones"]


def _guardar_sesion(entreno: dict) -> None:
    resumen = entreno["resumen"]
    try:
        fila = (cuentas.sb().table(TABLA).insert({
            "rutina_id": entreno["rutina_id"],
            "inicio": entreno["inicio"].isoformat(),
            "fin": entreno["fin"].isoformat(),
            **resumen,
        }).execute().data)
        entreno["sesion_id"] = fila[0]["id"] if fila else None
    except Exception as error:
        entreno["sesion_id"] = None
        if not _falta_la_tabla(error):
            entreno["error"] = "No se ha podido guardar el entrenamiento. Inténtalo más tarde."


# ---------------------------------------------------------------- acciones (botones)
def empezar(rutina_id: str) -> None:
    """Abre la pantalla de entrenar. Si ya estaba entrenando esa rutina, la continúa."""
    actual = st.session_state.get("entreno")
    if not actual or actual["rutina_id"] != rutina_id or actual["fase"] != "entrenando":
        for clave in [c for c in st.session_state if str(c).startswith("serie_")]:
            del st.session_state[clave]
        st.session_state.entreno = {"rutina_id": rutina_id, "fase": "entrenando",
                                    "inicio": datetime.now(timezone.utc)}
    st.session_state.seccion = "entrenar"


def _salir() -> None:
    st.session_state.pop("entreno", None)
    st.session_state.seccion = "inicio"


def _finalizar(ejercicios: list[tuple[str, int]]) -> None:
    entreno = st.session_state.entreno
    hechas = [len(st.session_state.get(f"serie_{i}") or []) for i in range(len(ejercicios))]
    entreno["fin"] = datetime.now(timezone.utc)
    entreno["resumen"] = calcular_resumen(ejercicios, hechas, entreno["inicio"], entreno["fin"])
    entreno["fase"] = "resumen"
    entreno["valoracion"] = None
    _guardar_sesion(entreno)


def _valorar(valoracion: str | None) -> None:
    entreno = st.session_state.entreno
    entreno["valoracion"] = valoracion or "saltada"
    if not valoracion:
        return
    anteriores = valoraciones_recientes()  # se leen antes de guardar la nueva, para no contarla dos veces
    if entreno.get("sesion_id"):
        try:
            (cuentas.sb().table(TABLA).update({"valoracion": valoracion})
             .eq("id", entreno["sesion_id"]).execute())
        except Exception:
            entreno["error"] = "No se ha podido guardar la valoración. Inténtalo más tarde."
    anteriores.append(valoracion)


# ---------------------------------------------------------------- lo que se ve
def boton_empezar(rutina: dict, clave: str) -> None:
    """Botón para empezar una rutina (solo si ya tiene ejercicios)."""
    if not ejercicios_de(rutina):
        return
    actual = st.session_state.get("entreno") or {}
    seguir = actual.get("rutina_id") == rutina["id"] and actual.get("fase") == "entrenando"
    st.button("▶️ Continuar rutina" if seguir else "▶️ Empezar rutina", key=f"empezar_{clave}",
              type="primary", use_container_width=True, on_click=empezar, args=(rutina["id"],))


def aviso_ajuste(pesa: dict) -> None:
    """En Inicio: cómo se ajusta la rutina de hoy según la última valoración."""
    texto = recomendacion(pesa, valoraciones_recientes())
    if texto:
        st.info(texto)


def _pantalla_entrenar(rutina: dict) -> None:
    ejercicios = ejercicios_de(rutina)
    estilos.titulo(rutina["nombre"], "Marca cada serie cuando la termines.")

    hechas = [len(st.session_state.get(f"serie_{i}") or []) for i in range(len(ejercicios))]
    total = sum(s for _, s in ejercicios)
    st.progress(sum(hechas) / total if total else 0, text=f"{sum(hechas)} de {total} series")

    for i, (nombre, series) in enumerate(ejercicios):
        st.pills(f"**{i + 1}. {nombre}**", [f"Serie {n}" for n in range(1, series + 1)],
                 selection_mode="multi", key=f"serie_{i}")

    st.write("")
    faltan = total - sum(hechas)
    if faltan:
        st.caption(f"Te faltan {faltan} series. Puedes finalizar igualmente y verás un resumen parcial.")
    st.button("🏁 Finalizar rutina", type="primary", use_container_width=True,
              on_click=_finalizar, args=(ejercicios,))
    st.button("Salir sin guardar", type="tertiary", on_click=_salir)


def _pantalla_resumen(rutina: dict, pesa: dict) -> None:
    entreno = st.session_state.entreno
    r = entreno["resumen"]
    if r["estado"] == "Completa":
        estilos.titulo("¡Rutina terminada! 🎉", f"Has completado «{rutina['nombre']}».")
    else:
        estilos.titulo("Rutina finalizada 👏",
                       f"Has hecho {r['series_hechas']} de {r['series_total']} series. ¡Cada serie cuenta!")

    c1, c2, c3 = st.columns(3)
    c1.metric("Ejercicios completados", f"{r['ejercicios_completados']} de {r['ejercicios_total']}", border=True)
    c2.metric("Series", f"{r['series_hechas']} de {r['series_total']}", border=True)
    c3.metric("Duración total", f"{r['duracion_min']} min", border=True)

    if entreno.get("error"):
        st.warning(entreno["error"])

    if entreno["valoracion"] is None:
        st.subheader("¿Cómo te ha resultado?")
        columnas = st.columns(3)
        for col, (valor, texto) in zip(columnas, VALORACIONES):
            col.button(texto, key=f"valorar_{valor}", use_container_width=True,
                       on_click=_valorar, args=(valor,))
        st.button("Saltar", type="tertiary", on_click=_valorar, args=(None,))
        return

    if entreno["valoracion"] != "saltada":
        st.success(f"¡Gracias! Hemos guardado tu valoración: **{entreno['valoracion'].lower()}**.")
        texto = recomendacion(pesa, valoraciones_recientes())
        if texto:
            st.info(texto)
    st.button("Volver al inicio", type="primary", use_container_width=True, on_click=_salir)


def mostrar(pesa: dict) -> None:
    entreno = st.session_state.get("entreno")
    rutina = datos.rutina_por_id(entreno["rutina_id"]) if entreno else None
    if not rutina:
        st.info("Elige una rutina y pulsa «▶️ Empezar rutina».")
        return
    if entreno["fase"] == "entrenando":
        _pantalla_entrenar(rutina)
    else:
        _pantalla_resumen(rutina, pesa)
