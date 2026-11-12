"""Pesas y rutinas, leídas de Supabase (tablas `pesas` y `rutinas`).

Las dos tablas se pueden leer sin iniciar sesión (política «lectura pública»).

VARIAS RUTINAS POR PESA, sin cambiar la base de datos: el peso va en el código
de la rutina. R03 = pesa de 3 kg, R03-2 = otra rutina de 3 kg, R10-2 = de 10 kg…
Se guardan en memoria 60 segundos para no consultar Supabase a cada clic:
si María cambia una rutina en Supabase, aparece en la web en menos de un minuto.
"""
import re

import streamlit as st
from supabase import Client, create_client

NIVELES = ["Principiante", "Intermedio", "Avanzado"]

# Tienda (precios de ejemplo; no están en la base de datos)
PRODUCTOS = [
    {"peso_kg": 3, "precio": 19.90, "nivel": "Principiante", "texto": "Ideal para empezar y coger técnica."},
    {"peso_kg": 5, "precio": 24.90, "nivel": "Principiante", "texto": "Para seguir progresando desde casa."},
    {"peso_kg": 10, "precio": 39.90, "nivel": "Intermedio", "texto": "Fuerza general para todo el cuerpo."},
    {"peso_kg": 15, "precio": 54.90, "nivel": "Avanzado", "texto": "Para quien ya domina la técnica."},
]


@st.cache_resource
def _cliente_publico() -> Client:
    datos = st.secrets["supabase"]
    return create_client(datos["url"], datos["key"])


@st.cache_data(ttl=60, show_spinner=False)
def _pesas() -> dict:
    filas = _cliente_publico().table("pesas").select("*").execute().data
    return {p["codigo"]: p for p in filas}


def peso_del_codigo(rutina_id: str) -> int | None:
    """El peso va en el código de la rutina: R03 y R03-2 son de 3 kg, R10-B de 10 kg…"""
    numero = re.match(r"^R(\d+)", rutina_id or "")
    return int(numero.group(1)) if numero else None


@st.cache_data(ttl=60, show_spinner=False)
def _rutinas() -> list[dict]:
    filas = _cliente_publico().table("rutinas").select("*").order("id").execute().data
    peso_de_rutina = {p["rutina_id"]: p["peso_kg"] for p in _pesas().values()}
    for r in filas:
        # 1.º el peso del código (R03-2 → 3 kg); si no lo tiene, el de la pesa que la tiene asignada
        r["peso_kg"] = peso_del_codigo(r["id"]) or peso_de_rutina.get(r["id"])
    return filas


def obtener_pesa(codigo: str | None) -> dict | None:
    """La pesa con ese código (el del QR), o None si no existe."""
    return _pesas().get(codigo) if codigo else None


def listar_pesas() -> list[dict]:
    return sorted(_pesas().values(), key=lambda p: p["peso_kg"])


def obtener_rutina(rutina_id: str | None) -> dict | None:
    return next((r for r in _rutinas() if r["id"] == rutina_id), None) if rutina_id else None


rutina_por_id = obtener_rutina


def rutinas_de_pesa(peso_kg: int) -> list[dict]:
    """Rutinas que se pueden hacer con una pesa."""
    return [r for r in _rutinas() if r.get("peso_kg") == peso_kg]


def rutina_de_objetivo(peso_kg: int, objetivo: str | None) -> dict | None:
    """La rutina de esa pesa pensada para el objetivo de la persona.
    El objetivo va en el nombre: «Full Body 3 - Perder peso»."""
    if not objetivo:
        return None
    return next((r for r in rutinas_de_pesa(peso_kg)
                 if objetivo.lower() in r["nombre"].lower()), None)


def rutinas_de_nivel(nivel: str) -> list[dict]:
    """Rutinas asignadas a un nivel, ordenadas por peso."""
    return sorted((r for r in _rutinas() if r["nivel"] == nivel),
                  key=lambda r: (r.get("peso_kg") or 0, r["id"]))


def pesa_para_usuario(usuario: dict) -> dict | None:
    """La pesa que se usa cuando alguien entra sin escanear un QR:
    la de su perfil (la que escaneó al registrarse) o, si no tiene, la primera de su nivel."""
    pesas = listar_pesas()
    propia = next((p for p in pesas if p["peso_kg"] == usuario.get("peso_pesa_kg")), None)
    if propia:
        return propia
    nivel = usuario.get("nivel")
    de_su_nivel = next((p for p in pesas if (obtener_rutina(p["rutina_id"]) or {}).get("nivel") == nivel), None)
    return de_su_nivel or (pesas[0] if pesas else None)


def comparar_nivel(nivel_usuario: str, nivel_pesa: str) -> int:
    """<0 si la pesa es más exigente que su nivel, >0 si se le queda corta, 0 si encaja."""
    return NIVELES.index(nivel_usuario) - NIVELES.index(nivel_pesa)
