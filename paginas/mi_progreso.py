"""PVBPQAE-97 · Mi progreso (Isabel).

Resumen de todo lo que ha entrenado la persona, para todos (con o sin Premium):
- Kilos levantados en total, entrenamientos hechos y minutos totales.
- «Tu evolución»: entrenamientos por semana (últimas 8 semanas).
- «Últimos entrenamientos», con un botón para ver el historial completo.
Si todavía no ha terminado ninguna rutina, sale un mensaje para animarle a empezar.

Los datos salen de la tabla «sesiones_entrenamiento» (PVBPQAE-31), donde cada persona
solo ve las suyas (RLS). No hace falta crear nada nuevo en Supabase.

Los kilos se calculan así: peso de la pesa de la rutina × repeticiones de cada serie,
según las series que marcó en esa sesión (los ejercicios por tiempo, como la plancha, no suman).
"""
import re
from datetime import datetime, timedelta, timezone

import streamlit as st

from comun import cuentas, datos, estilos
from paginas import entrenar

TABLA = "sesiones_entrenamiento"
SEMANAS = 8
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

try:
    from zoneinfo import ZoneInfo
    ZONA = ZoneInfo("Europe/Madrid")
except Exception:  # si el servidor no tiene zonas horarias, se usa UTC
    ZONA = timezone.utc

# Iconos (líneas finas, color naranja)
_SVG = ('<svg viewBox="0 0 24 24" width="{t}" height="{t}" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{d}</svg>')
ICONOS = {
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "reloj": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "subida": '<path d="m3 17 6-6 4 4 8-8"/><path d="M14 7h7v7"/>',
    "calendario": '<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "pesa": '<path d="M6.5 6.5v11M17.5 6.5v11M3 9v6M21 9v6M6.5 12h11"/>',
}


def icono(nombre: str, tamano: int = 18) -> str:
    return _SVG.format(t=tamano, d=ICONOS[nombre])


CSS = """
<style>
  .prog-hero {background:linear-gradient(135deg,#EA580C,#C2410C); color:#fff; border-radius:20px;
              padding:1.6rem 1rem 1.3rem; text-align:center; margin-bottom:.9rem;
              box-shadow:0 8px 24px rgba(194,65,12,.22);}
  .prog-hero .kg {font-size:2.9rem; font-weight:800; line-height:1.05;}
  .prog-hero .txt {font-weight:600; margin-top:.35rem;}
  .prog-hero .chip {display:inline-block; margin-top:.7rem; padding:.18rem .75rem; border-radius:999px;
                    background:rgba(0,0,0,.2); font-size:.78rem; font-weight:700;}
  .prog-cifras {display:grid; grid-template-columns:1fr 1fr; gap:.7rem; margin-bottom:.9rem;}
  .prog-caja {border:1px solid #FBD9C0; border-radius:16px; padding:.9rem 1rem; background:#fff;}
  .prog-cifra {display:flex; align-items:center; gap:.75rem;}
  .prog-icono {width:2.3rem; height:2.3rem; border-radius:50%; background:#FFEDD5; color:#C2410C;
               display:flex; align-items:center; justify-content:center; flex-shrink:0;}
  .prog-num {font-size:1.6rem; font-weight:800; line-height:1.1; color:#1F2937;}
  .prog-num small {font-size:.9rem; font-weight:600;}
  .prog-etq {font-size:.8rem; opacity:.7;}
  .prog-cab {display:flex; align-items:flex-start; gap:.75rem; margin-bottom:.8rem;}
  .prog-cab .t {font-weight:800; font-size:1.05rem; color:#1F2937;}
  .prog-cab .s {font-size:.8rem; opacity:.7;}
  .prog-leyenda {margin-left:auto; font-size:.72rem; opacity:.8; white-space:nowrap;}
  .prog-leyenda i {display:inline-block; width:.6rem; height:.6rem; border-radius:2px;
                   background:#9A3412; margin-right:.25rem;}
  .prog-graf {display:flex; align-items:flex-end; gap:.35rem; height:150px;
              border-bottom:1px solid #E5E7EB; padding-top:1.2rem;}
  .prog-col {flex:1; display:flex; flex-direction:column; align-items:center; justify-content:flex-end;
             height:100%; min-width:0;}
  .prog-col .v {font-size:.75rem; font-weight:700; margin-bottom:.15rem; color:#1F2937;}
  .prog-col .b {width:100%; border-radius:6px 6px 0 0; background:#EA580C;}
  .prog-col.hoy .b {background:#9A3412;}
  .prog-fechas {display:flex; gap:.35rem; margin-top:.3rem;}
  .prog-fechas div {flex:1; text-align:center; font-size:.68rem; line-height:1.15; opacity:.75; min-width:0;}
  .prog-fechas div.hoy {font-weight:800; opacity:1;}
  .prog-nota {font-size:.72rem; opacity:.65; margin-top:.6rem;}
  .prog-fila {display:flex; align-items:center; gap:.75rem; padding:.6rem 0;
              border-bottom:1px solid #F3E8DE;}
  .prog-fila:last-child {border-bottom:none;}
  .prog-fila .ic {width:2.3rem; height:2.3rem; border-radius:10px; background:#FFEDD5; color:#C2410C;
                  display:flex; align-items:center; justify-content:center; flex-shrink:0;}
  .prog-fila .n {font-weight:700; font-size:.92rem; color:#1F2937;}
  .prog-fila .d {font-size:.78rem; opacity:.7;}
  .prog-fila .ok {margin-left:auto; width:1.7rem; height:1.7rem; border-radius:50%; background:#FFEDD5;
                  color:#C2410C; display:flex; align-items:center; justify-content:center; flex-shrink:0;}
  .prog-fila .ok.parcial {background:#F3F4F6; color:#6B7280; font-size:.7rem; font-weight:700;
                          width:auto; padding:0 .5rem; border-radius:999px;}
  .prog-vacio {text-align:center; padding-bottom:.4rem;}
  .prog-vacio .ic {width:3.4rem; height:3.4rem; border-radius:50%; background:#fff; color:#C2410C;
                   display:flex; align-items:center; justify-content:center; margin:0 auto .9rem;}
  .prog-vacio .t {font-weight:800; font-size:1.25rem; color:#1F2937;}
  .prog-vacio .s {font-size:.9rem; opacity:.75; margin:.4rem auto 0; max-width:26rem;}
  .st-key-progreso_ultimos, .st-key-progreso_vacio {border:1px solid #FBD9C0; border-radius:16px;
      padding:1rem; background:#fff;}
  .st-key-progreso_vacio {border:1.5px dashed #FBC9A6; background:#FFF4EC; border-radius:20px;
      padding:1.8rem 1.4rem 1.4rem;}
  .st-key-progreso_empezar {max-width:22rem; margin:0 auto;}
  .st-key-progreso_historial button, .st-key-progreso_empezar button {min-height:2.7rem;}
  .st-key-progreso_historial button {border:1.5px solid #C2410C; color:#C2410C;}
</style>
"""


# ---------------------------------------------------------------- cálculos
def repeticiones(ejercicio: str) -> int:
    """Repeticiones de UNA serie de un ejercicio (0 si va por tiempo, como «Plancha 3x30 s»).
    «Sentadilla 3x15» → 15 · «Remo 3x10 por lado» → 20 · «Sentadilla 15 repeticiones» → 15."""
    texto = ejercicio.lower()
    if re.search(r"\d+\s*(s|seg|segundos|min)\b", texto) and not re.search(r"repeticiones", texto):
        return 0
    por_lado = 2 if re.search(r"por (lado|pierna|brazo)", texto) else 1
    series_x_reps = re.findall(r"\d+\s*x\s*(\d+)", texto)
    if series_x_reps:
        return int(series_x_reps[-1]) * por_lado
    numero = re.search(r"(\d+)\s*(repeticiones|reps|por (lado|pierna|brazo))", texto)
    return int(numero.group(1)) * por_lado if numero else 0


def kilos_de_sesion(sesion: dict) -> float:
    """Kilos de una sesión: peso × repeticiones de la rutina completa × parte de las series hechas."""
    rutina = datos.rutina_por_id(sesion.get("rutina_id"))
    if not rutina:
        return 0
    peso = rutina.get("peso_kg") or datos.peso_del_codigo(rutina["id"]) or 0
    ejercicios = entrenar.ejercicios_de(rutina)
    reps_rutina = sum(series * repeticiones(nombre) for nombre, series in ejercicios)
    total = sesion.get("series_total") or sum(s for _, s in ejercicios) or 1
    parte = min(1, (sesion.get("series_hechas") or 0) / total)
    return peso * reps_rutina * parte


def fecha_local(texto: str) -> datetime:
    return datetime.fromisoformat(texto.replace("Z", "+00:00")).astimezone(ZONA)


def por_semana(sesiones: list[dict], hoy: datetime) -> list[tuple[datetime, int]]:
    """(lunes de la semana, entrenamientos) de las últimas SEMANAS semanas, de la más antigua a esta."""
    lunes_actual = (hoy - timedelta(days=hoy.weekday())).date()
    semanas = [lunes_actual - timedelta(weeks=n) for n in range(SEMANAS - 1, -1, -1)]
    cuenta = {s: 0 for s in semanas}
    for s in sesiones:
        dia = fecha_local(s["fin"]).date()
        lunes = dia - timedelta(days=dia.weekday())
        if lunes in cuenta:
            cuenta[lunes] += 1
    return [(s, cuenta[s]) for s in semanas]


def kilos_texto(kilos: float) -> str:
    return f"{round(kilos):,}".replace(",", ".")


# ---------------------------------------------------------------- Supabase
def _sesiones() -> list[dict] | None:
    """Entrenamientos de la persona (el más reciente primero). None si no se han podido leer."""
    try:
        return (cuentas.sb().table(TABLA)
                .select("rutina_id, fin, duracion_min, series_hechas, series_total, estado")
                .order("fin", desc=True).execute().data) or []
    except Exception as error:
        return [] if entrenar._falta_la_tabla(error) else None


# ---------------------------------------------------------------- lo que se ve
def _empezar_primera(pesa: dict | None) -> None:
    usuario = cuentas.usuario_actual() or {}
    rutina = None
    if pesa:
        rutina = (datos.rutina_de_objetivo(pesa["peso_kg"], usuario.get("objetivo"))
                  or datos.rutina_por_id(pesa.get("rutina_id")))
    if rutina and entrenar.ejercicios_de(rutina):
        entrenar.empezar(rutina["id"])
    else:
        st.session_state.seccion = "inicio"


def _cambiar_historial() -> None:
    st.session_state.progreso_todo = not st.session_state.get("progreso_todo", False)


def _sin_entrenamientos(pesa: dict | None) -> None:
    estilos.titulo("Mi progreso", "Todo lo que has entrenado, en un solo vistazo.")
    with st.container(key="progreso_vacio"):
        st.markdown(
            f'<div class="prog-vacio"><div class="ic">{icono("pesa", 26)}</div>'
            '<div class="t">Tu primera rutina te espera</div>'
            '<div class="s">Cuando termines una, aquí verás tus entrenamientos, tus minutos y '
            'los kilos que levantes. Empieza cuando quieras, a tu ritmo.</div></div>',
            unsafe_allow_html=True)
        st.button("Empezar mi primera rutina", key="progreso_empezar", type="primary",
                  use_container_width=True, on_click=_empezar_primera, args=(pesa,))


def _grafico(sesiones: list[dict], hoy: datetime) -> str:
    semanas = por_semana(sesiones, hoy)
    maximo = max([n for _, n in semanas] + [1])
    columnas, fechas = "", ""
    for i, (lunes, n) in enumerate(semanas):
        hoy_clase = " hoy" if i == len(semanas) - 1 else ""
        alto = 100 * n / maximo
        columnas += (f'<div class="prog-col{hoy_clase}"><div class="v">{n if n else ""}</div>'
                     f'<div class="b" style="height:{alto:.0f}%"></div></div>')
        fechas += f'<div class="{hoy_clase.strip()}">{lunes.day}<br>{MESES[lunes.month - 1]}</div>'
    return (f'<div class="prog-caja"><div class="prog-cab"><div class="prog-icono">{icono("subida")}</div>'
            '<div><div class="t">Tu evolución</div><div class="s">Entrenamientos por semana</div></div>'
            '<div class="prog-leyenda"><i></i>Esta semana</div></div>'
            f'<div class="prog-graf">{columnas}</div><div class="prog-fechas">{fechas}</div>'
            f'<div class="prog-nota">Cada barra es una semana (empieza el lunes). Últimas {SEMANAS} semanas.</div>'
            '</div>')


def _fila(sesion: dict) -> str:
    rutina = datos.rutina_por_id(sesion.get("rutina_id"))
    nombre = rutina["nombre"] if rutina else "Rutina"
    dia = fecha_local(sesion["fin"])
    fecha = f"{dia.day} {MESES[dia.month - 1]}"
    if sesion.get("estado") == "Parcial":
        marca = '<div class="ok parcial">Parcial</div>'
    else:
        marca = f'<div class="ok">{icono("check", 15)}</div>'
    return (f'<div class="prog-fila"><div class="ic">{icono("pesa")}</div>'
            f'<div><div class="n">{nombre}</div>'
            f'<div class="d">{fecha} · {sesion.get("duracion_min") or 0} min</div></div>{marca}</div>')


def mostrar(pesa: dict | None = None) -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    sesiones = _sesiones()
    if sesiones is None:
        estilos.titulo("Mi progreso")
        st.warning("No hemos podido cargar tu progreso. Inténtalo de nuevo en un momento.")
        st.button("Reintentar", key="progreso_reintentar")
        return
    if not sesiones:
        _sin_entrenamientos(pesa)
        return

    estilos.titulo("Mi progreso", "Aquí tienes un resumen de todo lo que has entrenado. ¡Sigue así!")
    kilos = sum(kilos_de_sesion(s) for s in sesiones)
    minutos = sum(s.get("duracion_min") or 0 for s in sesiones)
    st.markdown(
        f'<div class="prog-hero"><div class="kg">{kilos_texto(kilos)} kg</div>'
        '<div class="txt">Kilos levantados en total</div><div class="chip">Cada serie suma</div></div>'
        '<div class="prog-cifras">'
        f'<div class="prog-caja prog-cifra"><div class="prog-icono">{icono("check")}</div>'
        f'<div><div class="prog-num">{len(sesiones)}</div><div class="prog-etq">Entrenamientos hechos</div></div></div>'
        f'<div class="prog-caja prog-cifra"><div class="prog-icono">{icono("reloj")}</div>'
        f'<div><div class="prog-num">{minutos} <small>min</small></div><div class="prog-etq">Minutos totales</div></div></div>'
        '</div>' + _grafico(sesiones, datetime.now(ZONA)),
        unsafe_allow_html=True)
    st.write("")

    todo = st.session_state.get("progreso_todo", False)
    with st.container(key="progreso_ultimos"):
        lista = sesiones if todo else sesiones[:5]
        st.markdown(
            f'<div class="prog-cab"><div class="prog-icono">{icono("calendario")}</div>'
            f'<div><div class="t">{"Historial completo" if todo else "Últimos entrenamientos"}</div></div></div>'
            + "".join(_fila(s) for s in lista),
            unsafe_allow_html=True)
        if len(sesiones) > 5:
            st.button("Ver menos ↑" if todo else "Ver historial completo →", key="progreso_historial",
                      use_container_width=True, on_click=_cambiar_historial)
    st.caption("Se actualiza cada vez que terminas una rutina. Los kilos se calculan con el peso "
               "de la pesa, las repeticiones y las series que marcas.")
