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

PVBPQAE-28 · Temporizador de descanso (Javier): al marcar una serie arranca una cuenta atrás
(según el objetivo de la rutina), con «+30 s» y «Saltar», y un pitido y vibración al terminar.
Es para todos los usuarios (con o sin Premium) y no usa Supabase.
"""
import json
import re
import time
from datetime import datetime, timezone

import streamlit as st
import streamlit.components.v1 as components

from comun import cuentas, datos, estilos
from paginas import tecnica

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


# ---------------------------------------------------------------- PVBPQAE-28 · descanso
# Segundos de descanso entre series según el objetivo de la rutina (va en su nombre)
DESCANSOS = {"Ganar fuerza": 90, "Tonificar": 60, "Salud general": 45,
             "Constancia": 45, "Perder peso": 30}


def segundos_de_descanso(rutina: dict) -> int:
    """«Full Body 2 - Ganar fuerza» → 90. Si el nombre no dice el objetivo, 60."""
    nombre = (rutina.get("nombre") or "").lower()
    return next((s for objetivo, s in DESCANSOS.items() if objetivo.lower() in nombre), 60)


def siguiente_serie(ejercicios: list[tuple[str, int]], hechas: list[int]) -> str | None:
    """Qué toca después: «Sentadilla goblet, serie 3». None si ya están todas."""
    for (nombre, series), h in zip(ejercicios, hechas):
        if h < series:
            return f"{tecnica.nombre_base(nombre)}, serie {h + 1}"
    return None


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


def _serie_marcada(i: int, ejercicios: list[tuple[str, int]], segundos: int) -> None:
    """PVBPQAE-28: al marcar una serie (no al desmarcarla) empieza el descanso."""
    entreno = st.session_state.entreno
    marcadas = entreno.setdefault("marcadas", {})
    ahora = len(st.session_state.get(f"serie_{i}") or [])
    antes = marcadas.get(i, 0)
    marcadas[i] = ahora
    if ahora <= antes:
        return
    hechas = [len(st.session_state.get(f"serie_{j}") or []) for j in range(len(ejercicios))]
    siguiente = siguiente_serie(ejercicios, hechas)
    if not siguiente:  # era la última serie: no hay que descansar
        entreno.pop("descanso", None)
        return
    entreno["descanso"] = {"fin": time.time() + segundos, "total": segundos, "siguiente": siguiente}


def _alargar_descanso() -> None:
    descanso = st.session_state.entreno.get("descanso")
    if descanso:
        descanso["fin"] = max(descanso["fin"], time.time()) + 30
        descanso["total"] = max(descanso["total"], round(descanso["fin"] - time.time()))


def _saltar_descanso() -> None:
    st.session_state.entreno.pop("descanso", None)


def _salir() -> None:
    st.session_state.pop("entreno", None)
    st.session_state.seccion = "inicio"


def _finalizar(ejercicios: list[tuple[str, int]]) -> None:
    entreno = st.session_state.entreno
    hechas = [len(st.session_state.get(f"serie_{i}") or []) for i in range(len(ejercicios))]
    entreno.pop("descanso", None)  # PVBPQAE-28
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


CUENTA_ATRAS = """
<div id="caja" style="font-family:'Source Sans Pro',Arial,sans-serif;border:2px solid #EA580C;
     border-radius:14px;padding:10px 12px;text-align:center;background:#FFF4EC;color:#1F2937">
  <div style="font-size:14px;color:#6B7280">⏱️ Descansa · siguiente: <b id="sig"></b></div>
  <div id="tiempo" style="font-size:42px;font-weight:700;color:#EA580C;line-height:1.2">0:00</div>
  <div style="height:6px;background:#FED7AA;border-radius:3px">
    <div id="barra" style="height:6px;background:#EA580C;border-radius:3px;width:100%"></div></div>
</div>
<script>
const datos = __DATOS__;
const fin = Date.now() + datos.restante * 1000;
document.getElementById("sig").textContent = datos.siguiente;
let avisado = datos.restante <= 0;
function pitido() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    [0, 0.3, 0.6].forEach(t => {
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.frequency.value = 880; o.connect(g); g.connect(ctx.destination);
      g.gain.setValueAtTime(0.3, ctx.currentTime + t);
      o.start(ctx.currentTime + t); o.stop(ctx.currentTime + t + 0.18);
    });
  } catch (e) {}
  try { navigator.vibrate([200, 100, 200]); } catch (e) {}
}
function pintar() {
  const quedan = Math.max(0, Math.ceil((fin - Date.now()) / 1000));
  const t = document.getElementById("tiempo");
  if (quedan > 0) {
    t.textContent = Math.floor(quedan / 60) + ":" + String(quedan % 60).padStart(2, "0");
  } else {
    t.textContent = "¡A por la siguiente! 💪";
    t.style.fontSize = "26px";
    document.getElementById("caja").style.background = "#FFEDD5";
    if (!avisado) { avisado = true; pitido(); }
  }
  document.getElementById("barra").style.width = (100 * quedan / datos.total) + "%";
}
pintar();
setInterval(pintar, 250);
</script>
"""


def temporizador() -> None:
    """PVBPQAE-28: la cuenta atrás del descanso, con «+30 s» y «Saltar»."""
    descanso = st.session_state.entreno.get("descanso")
    if not descanso:
        return
    restante = descanso["fin"] - time.time()
    if restante < -120:  # terminó hace rato: ya no se enseña
        st.session_state.entreno.pop("descanso", None)
        return
    datos_js = {"restante": round(restante, 1), "total": descanso["total"],
                "siguiente": descanso["siguiente"]}
    components.html(CUENTA_ATRAS.replace("__DATOS__", json.dumps(datos_js)), height=128)
    st.html("""<style>
      .st-key-descanso [data-testid="stHorizontalBlock"] {flex-wrap:nowrap; gap:.5rem;}
      .st-key-descanso [data-testid="stHorizontalBlock"] > div {min-width:0 !important;}
    </style>""")
    with st.container(key="descanso"):
        mas, saltar = st.columns(2)
        mas.button("➕ 30 s", key="descanso_mas", use_container_width=True, on_click=_alargar_descanso)
        saltar.button("⏭️ Saltar", key="descanso_saltar", use_container_width=True,
                      on_click=_saltar_descanso)


def _pantalla_entrenar(rutina: dict) -> None:
    ejercicios = ejercicios_de(rutina)
    estilos.titulo(rutina["nombre"], "Marca cada serie cuando la termines.")

    hechas = [len(st.session_state.get(f"serie_{i}") or []) for i in range(len(ejercicios))]
    total = sum(s for _, s in ejercicios)
    st.progress(sum(hechas) / total if total else 0, text=f"{sum(hechas)} de {total} series")
    temporizador()  # PVBPQAE-28

    segundos = segundos_de_descanso(rutina)
    for i, (nombre, series) in enumerate(ejercicios):
        st.pills(f"**{i + 1}. {nombre}**", [f"Serie {n}" for n in range(1, series + 1)],
                 selection_mode="multi", key=f"serie_{i}",
                 on_change=_serie_marcada, args=(i, ejercicios, segundos))  # PVBPQAE-28
        tecnica.boton(nombre, f"ent_{i}")  # PVBPQAE-12: «Cómo se hace»

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
