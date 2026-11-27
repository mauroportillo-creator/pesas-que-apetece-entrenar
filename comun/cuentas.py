"""La persona que ha iniciado sesión: su perfil y sus rutinas guardadas.

- El perfil (nombre, edad, nivel, objetivo…) está en la tabla «Registro de usuarios»;
  cada persona solo ve y cambia el suyo (RLS).
- Registro, inicio de sesión y recuperar contraseña están en comun/autenticacion.py (PVBPQAE-46).

Los datos de conexión con Supabase están en .streamlit/secrets.toml (no se sube a GitHub).
"""
from datetime import date

import streamlit as st
from supabase import Client, create_client

TABLA = "Registro de usuarios"


def sb() -> Client:
    """Un cliente de Supabase por persona conectada (guarda su sesión)."""
    if "sb" not in st.session_state:
        datos = st.secrets["supabase"]
        st.session_state.sb = create_client(datos["url"], datos["key"])
    return st.session_state.sb


def usuario_actual() -> dict | None:
    return st.session_state.get("usuario")


def cerrar_sesion() -> None:
    try:
        sb().auth.sign_out()
    except Exception:
        pass
    st.session_state.pop("usuario", None)


# ---------------------------------------------------------------- perfil
def cargar_perfil() -> None:
    """Lee el perfil de la persona que acaba de iniciar sesión."""
    usuario_auth = sb().auth.get_user().user
    fila = (sb().table(TABLA).select("*").eq("auth_id", usuario_auth.id)
            .limit(1).execute().data)
    perfil = fila[0] if fila else {}
    st.session_state.usuario = {
        "id_usuario": perfil.get("id_usuario"),
        "nombre": perfil.get("Nombre") or "",
        "apellidos": perfil.get("apellidos") or "",
        "correo": usuario_auth.email,
        "edad": perfil.get("edad"),
        "genero": perfil.get("genero"),
        "peso_pesa_kg": perfil.get("peso_pesa_kg"),
        "nivel": perfil.get("nivel"),
        "objetivo": perfil.get("objetivo"),
        "plan": perfil.get("plan") or "Gratuito",  # PVBPQAE-93
        "fecha_suscripcion": perfil.get("fecha_suscripcion"),
        "fecha_fin_premium": perfil.get("fecha_fin_premium"),  # PVBPQAE-20: si canceló, hasta cuándo
        "fecha_terminos": perfil.get("fecha_terminos"),  # PVBPQAE-94: cuándo aceptó los términos
        # «Mis rutinas» (la estrella): tabla rutinas_guardadas
        "rutinas_guardadas": _leer_rutinas_guardadas(),
    }
    _quitar_premium_si_ha_terminado()  # PVBPQAE-20


def _actualizar_perfil(cambios: dict) -> None:
    sb().table(TABLA).update(cambios).eq("auth_id", sb().auth.get_user().user.id).execute()


def guardar_perfil(nivel: str, objetivo: str, respuestas: dict) -> None:
    """Guarda el resultado del cuestionario."""
    _actualizar_perfil({"nivel": nivel, "objetivo": objetivo})
    st.session_state.usuario.update(nivel=nivel, objetivo=objetivo)


def actualizar_datos(nombre: str, apellidos: str, nivel: str, objetivo: str) -> None:
    """Guarda los cambios de «Mis datos»."""
    _actualizar_perfil({"Nombre": nombre.strip(), "apellidos": apellidos.strip(),
                        "nivel": nivel, "objetivo": objetivo})
    st.session_state.usuario.update(nombre=nombre.strip(), apellidos=apellidos.strip(),
                                    nivel=nivel, objetivo=objetivo)


# ---------------------------------------------------------------- plan Premium (PVBPQAE-93)
# El plan está en la columna «plan» del perfil (Gratuito / Premium). La web no puede cambiarla
# directamente: lo hace la función hacerme_premium() de Supabase (8_suscripcion_premium.sql).
def es_premium() -> bool:
    """¿La persona que ha iniciado sesión tiene el plan Premium? (lo usan también 8, 10, 12, 20 y 98)"""
    usuario = usuario_actual()
    return bool(usuario) and usuario.get("plan") == "Premium" and not _premium_terminado(usuario)


# ---------------------------------------------------------------- cancelar Premium (PVBPQAE-20)
# Al cancelar no se quita Premium en el momento: se desactiva la renovación y se sigue teniendo
# hasta el día antes de la siguiente renovación mensual (columna «fecha_fin_premium»).
# Lo cambian las funciones cancelar_premium() y quitar_premium_terminado() de Supabase
# (12_cancelar_suscripcion.sql); la web no puede cambiar esas columnas directamente.
def _fecha(valor) -> date | None:
    return date.fromisoformat(str(valor)[:10]) if valor else None


def _premium_terminado(usuario: dict) -> bool:
    fin = _fecha(usuario.get("fecha_fin_premium"))
    return bool(fin) and fin < date.today()


def premium_cancelado() -> bool:
    """¿Ha cancelado la suscripción (sigue siendo Premium hasta fecha_fin_premium)?"""
    usuario = usuario_actual()
    return bool(usuario) and bool(usuario.get("fecha_fin_premium"))


def fin_de_acceso(hoy: date | None = None) -> date:
    """Último día de Premium si cancela hoy: el día antes de la siguiente renovación mensual.
    Es el mismo cálculo que hace cancelar_premium() en Supabase."""
    hoy = hoy or date.today()
    desde = _fecha((usuario_actual() or {}).get("fecha_suscripcion")) or hoy
    meses = 1
    while _sumar_meses(desde, meses) <= hoy:
        meses += 1
    return date.fromordinal(_sumar_meses(desde, meses).toordinal() - 1)


def _sumar_meses(dia: date, meses: int) -> date:
    """Suma meses como Postgres: el 31 de enero + 1 mes = 28 (o 29) de febrero."""
    mes = dia.month - 1 + meses
    anio, mes = dia.year + mes // 12, mes % 12 + 1
    for d in range(dia.day, 27, -1):
        try:
            return date(anio, mes, d)
        except ValueError:
            continue
    return date(anio, mes, min(dia.day, 28))


def cancelar_premium() -> str | None:
    """Desactiva la renovación. Devuelve un error o None."""
    try:
        fin = sb().rpc("cancelar_premium").execute().data
    except Exception:
        return "No se ha podido cancelar la suscripción. Inténtalo de nuevo más tarde."
    st.session_state.usuario["fecha_fin_premium"] = fin or fin_de_acceso().isoformat()
    return None


def _quitar_premium_si_ha_terminado() -> None:
    """Si ya pasó la fecha de fin, el plan vuelve a Gratuito también en Supabase."""
    usuario = usuario_actual()
    if usuario.get("plan") == "Premium" and _premium_terminado(usuario):
        try:
            sb().rpc("quitar_premium_terminado").execute()
        except Exception:
            pass  # es_premium() ya lo trata como gratuito
        usuario.update(plan="Gratuito", fecha_fin_premium=None)


def es_admin() -> bool:
    """¿La persona que ha iniciado sesión es del equipo? (tabla «administradores», PVBPQAE-95)"""
    usuario = usuario_actual()
    if not usuario:
        return False
    if "es_admin" not in usuario:
        try:
            usuario["es_admin"] = bool(sb().rpc("soy_admin").execute().data)
        except Exception:
            return False
    return usuario["es_admin"]


def hacerme_premium() -> str | None:
    """Cambia el plan a Premium y regala la tarjeta. Devuelve un error o None."""
    try:
        sb().rpc("hacerme_premium").execute()
    except Exception:
        return "No se ha podido activar el plan Premium. Inténtalo de nuevo más tarde."
    fila = (sb().table(TABLA).select("plan, fecha_suscripcion")
            .eq("auth_id", sb().auth.get_user().user.id).limit(1).execute().data)
    if fila:
        st.session_state.usuario.update(plan=fila[0]["plan"],
                                        fecha_suscripcion=fila[0]["fecha_suscripcion"],
                                        fecha_fin_premium=None)  # PVBPQAE-20: vuelve a renovarse
    st.session_state.usuario.pop("tarjeta_regalo", None)
    return None


def tarjeta_regalo() -> dict | None:
    """La tarjeta regalo de la persona (código, importe, si está usada) o None si no tiene."""
    usuario = usuario_actual()
    if "tarjeta_regalo" not in usuario:
        try:
            filas = (sb().table("tarjetas_regalo").select("codigo, importe, usada")
                     .limit(1).execute().data)
            usuario["tarjeta_regalo"] = filas[0] if filas else None
        except Exception:
            return None
    return usuario["tarjeta_regalo"]


# ---------------------------------------------------------------- mis rutinas (estrella)
# Se guardan en la tabla «rutinas_guardadas» (cada persona solo ve las suyas).
# Si esa tabla todavía no existe en Supabase, duran solo mientras la sesión está abierta.
def _falta_la_tabla(error: Exception) -> bool:
    texto = str(error).lower()
    return "pgrst205" in texto or "42p01" in texto or "could not find the table" in texto


def _leer_rutinas_guardadas() -> list[str]:
    try:
        filas = sb().table("rutinas_guardadas").select("rutina_id").order("fecha").execute().data
        return [f["rutina_id"] for f in filas]
    except Exception:
        return []


def guardar_rutina(rutina_id: str) -> str | None:
    """Guarda la rutina en «Mis rutinas». Devuelve un error o None."""
    guardadas = st.session_state.usuario["rutinas_guardadas"]
    if rutina_id in guardadas:
        return None
    try:
        sb().table("rutinas_guardadas").upsert({"rutina_id": rutina_id}).execute()
    except Exception as error:
        if not _falta_la_tabla(error):
            return "No se ha podido guardar la rutina. Inténtalo de nuevo."
    guardadas.append(rutina_id)
    return None


def quitar_rutina(rutina_id: str) -> str | None:
    """Quita la rutina de «Mis rutinas». Devuelve un error o None."""
    guardadas = st.session_state.usuario["rutinas_guardadas"]
    try:
        sb().table("rutinas_guardadas").delete().eq("rutina_id", rutina_id).execute()
    except Exception as error:
        if not _falta_la_tabla(error):
            return "No se ha podido quitar la rutina. Inténtalo de nuevo."
    if rutina_id in guardadas:
        guardadas.remove(rutina_id)
    return None
