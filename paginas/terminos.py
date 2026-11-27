"""PVBPQAE-94 · Términos y condiciones y política de privacidad (Mauro).

Se abren en una ventana con el botón «📄 Términos y condiciones», que está:
- en «Crea tu cuenta», junto a la casilla para aceptarlos (paginas/registro_login.py);
- en «Mis datos», con la fecha en que la persona los aceptó (paginas/mis_datos.py).
La fecha de aceptación la guarda Supabase al crear la cuenta (13_terminos_condiciones.sql).
"""
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

ACTUALIZADOS = "27/11/2026"

TEXTO = f"""
*Última actualización: {ACTUALIZADOS}.* «Pesas que apetece enseñar» es un proyecto académico
del equipo de CUNEF Universidad. Aquí te contamos qué datos guardamos, para qué y cómo borrarlos.

#### 1. Qué datos guardamos
- **Los que escribes al registrarte:** nombre, apellidos, correo, edad, género y el peso de la
  pesa que has escaneado.
- **Tu contraseña:** la guarda cifrada nuestro proveedor (Supabase). Nadie del equipo puede verla.
- **Tu nivel y tu objetivo**, que salen del cuestionario y puedes cambiar en «Mis datos».
- **Tu actividad en la app:** las rutinas que guardas con la estrella, los entrenamientos que
  terminas (rutina, día, minutos, series hechas y tu valoración), tu plan (gratuito o Premium)
  y tu tarjeta regalo.
- **La fecha en que aceptaste** estos términos.

#### 2. Para qué los usamos
- Recomendarte la rutina que encaja con tu pesa, tu nivel y tu objetivo.
- Guardar tus rutinas y enseñarte tu progreso.
- Gestionar tu plan Premium (el pago es simulado: no pedimos ni guardamos datos bancarios).
- Mejorar la app: el equipo ve estadísticas generales y la lista de usuarios **sin correos ni
  contraseñas**.

No vendemos ni compartimos tus datos con nadie y no los usamos para publicidad.

#### 3. Dónde se guardan y quién los ve
En Supabase, con reglas que hacen que **cada persona solo pueda ver y cambiar sus propios datos**.
Solo las 6 personas del equipo pueden ver las estadísticas generales.

#### 4. Tus derechos y cómo eliminar tu cuenta
- Puedes ver y cambiar tus datos en **Menú > 👤 Mis datos**.
- Para borrarlo todo: **Mis datos > 🗑️ Eliminar mi cuenta**. Se borran al momento tu cuenta,
  tu perfil, tus rutinas guardadas, tus entrenamientos y tu tarjeta regalo. No se puede deshacer.

#### 5. Uso de la app
Las rutinas son orientativas. Entrena a tu ritmo y, si tienes alguna lesión o duda de salud,
consulta antes con un profesional. Al crear tu cuenta aceptas estos términos.
"""


@st.dialog("Términos y condiciones y política de privacidad", width="large")
def _ventana() -> None:
    st.markdown(TEXTO)
    if st.button("Entendido", type="primary", use_container_width=True):
        st.rerun()


def boton(clave: str) -> None:
    """Botón que abre los términos en una ventana (escenario 3)."""
    if st.button("📄 Términos y condiciones", key=clave, type="tertiary"):
        _ventana()


def fecha_aceptacion(valor) -> str | None:
    """«27/11/2026» a partir de la fecha que guarda Supabase (o None si no hay)."""
    if not valor:
        return None
    try:
        return (datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
                .astimezone(ZoneInfo("Europe/Madrid")).strftime("%d/%m/%Y"))
    except (ValueError, KeyError):
        return None
