"""PVBPQAE-27 · Onboarding de nivel y objetivo (María Luz).

Cuestionario de María: una pregunta por pantalla, con barra de progreso.

Reglas:
- Preguntas 1 a 3: mayoría de A → Principiante, de B → Intermedio, de C → Avanzado.
- Pregunta 4: es el objetivo, no cuenta para el nivel.
- Empate (una A, una B y una C):
  · Si la pregunta 2 es C (domina los ejercicios básicos) → Intermedio.
  · Si no, mandan las preguntas 1 y 2 y se queda en el nivel más bajo de los dos.
    Por ejemplo, una A y una B en las preguntas 1 y 2 → Principiante.
- Avanzado solo con mayoría de C.
"""
import streamlit as st

from comun import cuentas, datos, estilos
from comun.navegacion import ir_a

PREGUNTAS = [
    {"texto": "¿Cómo te sientes al entrenar por tu cuenta?",
     "opciones": {"A": "Necesito que me guíen",
                  "B": "Tengo cierta autonomía, pero necesito instrucciones",
                  "C": "Sé seguir una rutina estructurada"}},
    {"texto": "¿Qué grado de dominio tienes de los ejercicios básicos "
              "(sentadilla, peso muerto, press militar, remo)?",
     "opciones": {"A": "No los conozco o no sé ejecutarlos",
                  "B": "Los conozco, pero necesito aprender la técnica",
                  "C": "Los ejecuto correctamente y con buena progresión de cargas"}},
    {"texto": "¿Has seguido alguna vez una rutina de fuerza?",
     "opciones": {"A": "No, nunca",
                  "B": "Sí, durante algunas semanas o meses",
                  "C": "Sí, durante más de un año"}},
    {"texto": "¿Cuál es tu objetivo principal al entrenar?",
     "opciones": {"A": "Tonificar",
                  "B": "Ganar fuerza",
                  "C": "Perder peso",
                  "D": "Salud general",
                  "E": "Constancia"},
     "es_objetivo": True},
]
OBJETIVOS = list(PREGUNTAS[3]["opciones"].values())
NIVEL_POR_LETRA = {"A": "Principiante", "B": "Intermedio", "C": "Avanzado"}


def calcular_nivel(respuestas: dict) -> str:
    """Nivel según la mayoría de letras en las preguntas 1 a 3."""
    letras = [respuestas[i] for i, p in enumerate(PREGUNTAS) if not p.get("es_objetivo")]
    for letra in "ABC":
        if letras.count(letra) >= 2:
            return NIVEL_POR_LETRA[letra]
    # Empate (una de cada):
    # si domina los ejercicios básicos (C en la pregunta 2), como mínimo Intermedio
    if respuestas[1] == "C":
        return "Intermedio"
    # si no, el nivel más bajo entre las preguntas 1 y 2
    return NIVEL_POR_LETRA[min(respuestas[0], respuestas[1])]


def _estado() -> dict:
    return st.session_state.setdefault("cuestionario", {"paso": 0, "respuestas": {}})


def empezar_de_nuevo() -> None:
    st.session_state.cuestionario = {"paso": 0, "respuestas": {}}


def _responder(paso: int, letra: str) -> None:
    estado = _estado()
    estado["respuestas"][paso] = letra
    estado["paso"] = paso + 1


def _anterior() -> None:
    _estado()["paso"] = max(0, _estado()["paso"] - 1)


def _listo(nivel: str, objetivo: str, respuestas: dict) -> None:
    cuentas.guardar_perfil(nivel, objetivo, {PREGUNTAS[i]["texto"]: PREGUNTAS[i]["opciones"][l]
                                             for i, l in respuestas.items()})
    empezar_de_nuevo()
    st.session_state.seccion = "rutinas"
    ir_a("principal")


def _barra_progreso(respondidas: int) -> None:
    porcentaje = round(respondidas / len(PREGUNTAS) * 100)
    st.write("")
    st.progress(porcentaje / 100, text=f"{porcentaje} % completado")


def _pantalla_pregunta(paso: int, respuestas: dict) -> None:
    pregunta = PREGUNTAS[paso]
    st.caption(f"Pregunta {paso + 1} de {len(PREGUNTAS)}")
    estilos.titulo(pregunta["texto"])
    for letra, texto in pregunta["opciones"].items():
        st.button(texto, key=f"p{paso}_{letra}", use_container_width=True,
                  type="primary" if respuestas.get(paso) == letra else "secondary",
                  on_click=_responder, args=(paso, letra))
    if paso > 0:
        st.button("← Anterior", type="tertiary", on_click=_anterior)
    _barra_progreso(len(respuestas))


def _pantalla_final(pesa: dict | None, respuestas: dict) -> None:
    nivel = calcular_nivel(respuestas)
    objetivo = PREGUNTAS[3]["opciones"][respuestas[3]]
    st.markdown(
        f'<div class="tarjeta-pesa"><div class="etiqueta">Tu nivel es</div>'
        f'<div class="peso" style="font-size:2.4rem;margin:.3rem 0">{nivel}</div>'
        f'<div class="nivel">Objetivo: {objetivo.lower()}</div></div>',
        unsafe_allow_html=True,
    )
    estilos.titulo("¡Cuestionario completado! 🎉",
                   "Te mostraremos las rutinas pensadas para tu nivel.")

    # Aviso de nivel (solo si ha escaneado una pesa; sin QR no hay pesa que comparar)
    nivel_pesa = datos.obtener_rutina(pesa["rutina_id"])["nivel"] if pesa else nivel
    diferencia = datos.comparar_nivel(nivel, nivel_pesa)
    if diferencia:
        recomendadas = " o ".join(f"{p['peso_kg']} kg" for p in datos.listar_pesas()
                                  if datos.obtener_rutina(p["rutina_id"])["nivel"] == nivel)
        motivo = "puede quedarse corta" if diferencia > 0 else "puede ser exigente"
        st.warning(f"La pesa que has escaneado ({pesa['peso_kg']} kg) es de nivel "
                   f"{nivel_pesa.lower()} y {motivo} para ti. Te recomendamos la de **{recomendadas}**, "
                   "aunque puedes continuar igualmente.")

    st.button("Listo", type="primary", use_container_width=True,
              on_click=_listo, args=(nivel, objetivo, dict(respuestas)))
    st.button("← Cambiar respuestas", type="tertiary", on_click=_anterior)
    _barra_progreso(len(PREGUNTAS))


def mostrar(pesa: dict) -> None:
    estado = _estado()
    if estado["paso"] < len(PREGUNTAS):
        _pantalla_pregunta(estado["paso"], estado["respuestas"])
    else:
        _pantalla_final(pesa, estado["respuestas"])
