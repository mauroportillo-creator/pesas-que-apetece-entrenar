"""La persona que ha iniciado sesión: su perfil y sus rutinas guardadas.

- El perfil (nombre, edad, nivel, objetivo…) está en la tabla «Registro de usuarios»;
  cada persona solo ve y cambia el suyo (RLS).
- Registro, inicio de sesión y recuperar contraseña están en comun/autenticacion.py (PVBPQAE-46).

Los datos de conexión con Supabase están en .streamlit/secrets.toml (no se sube a GitHub).
"""
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
        # «Mis rutinas» (la estrella): tabla rutinas_guardadas
        "rutinas_guardadas": _leer_rutinas_guardadas(),
    }


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
