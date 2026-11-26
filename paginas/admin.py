"""PVBPQAE-95 · Panel de administración (Marta).

Solo lo ven los 6 del equipo (tabla «administradores» y función soy_admin() de Supabase,
11_panel_administracion.sql). Cinco pestañas:
  📊 Estadísticas · 👥 Usuarios · 💪 Rutinas · 📘 Técnica · 🥗 Alimentación
Todo se lee y se guarda en Supabase con la sesión de quien está dentro: las reglas (RLS) solo
dejan hacerlo a los administradores. Nunca se usa la clave secreta (service_role).
"""
import re
from datetime import date, datetime, timedelta, timezone

import pandas as pd
import streamlit as st

from comun import cuentas, datos, estilos
from paginas.cuestionario import OBJETIVOS
from paginas.tecnica import nombre_base

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
NUEVA = "➕ Nueva rutina"


# ---------------------------------------------------------------- acceso a Supabase
def _leer(tabla: str, columnas: str = "*", orden: str | None = None, **filtros) -> list[dict]:
    consulta = cuentas.sb().table(tabla).select(columnas)
    for columna, valor in filtros.items():
        consulta = consulta.eq(columna, valor)
    if orden:
        consulta = consulta.order(orden)
    return consulta.execute().data


def _actualizar(tabla: str, cambios: dict, **filtros) -> str | None:
    try:
        consulta = cuentas.sb().table(tabla).update(cambios)
        for columna, valor in filtros.items():
            consulta = consulta.eq(columna, valor)
        consulta.execute()
    except Exception:
        return "No se ha podido guardar. Inténtalo de nuevo."
    return None


def _insertar(tabla: str, filas: dict | list[dict]) -> str | None:
    try:
        cuentas.sb().table(tabla).insert(filas).execute()
    except Exception:
        return "No se ha podido guardar. Inténtalo de nuevo."
    return None


def _resultado(error: str | None, ok: str) -> None:
    """Si ha ido bien, se vuelve a pintar el panel (con los datos nuevos) y sale el aviso arriba."""
    if error:
        st.error(error)
        return
    st.session_state.admin_aviso = ok
    st.rerun()


# ---------------------------------------------------------------- 📊 estadísticas
def _de_pago(usuario: dict) -> bool:
    """Premium en la web; los usuarios sintéticos (PVBPQAE-42) tienen «Mensual» o «Anual»."""
    return (usuario.get("plan") or "Gratuito") != "Gratuito"


def _contar(filas: list[dict], campo: str) -> pd.DataFrame:
    serie = pd.Series([f.get(campo) or "Sin dato" for f in filas]).value_counts()
    return serie.rename("Personas").to_frame()


def _estadisticas() -> None:
    usuarios = _leer("Registro de usuarios", "nivel, objetivo, plan, fecha_registro")
    sesiones = _leer("sesiones_entrenamiento", "rutina_id, valoracion")
    tarjetas = _leer("tarjetas_regalo", "usada")

    premium = sum(1 for u in usuarios if _de_pago(u))
    hace_7 = (date.today() - timedelta(days=7)).isoformat()
    nuevos = sum(1 for u in usuarios if str(u.get("fecha_registro") or "") >= hace_7)
    c1, c2 = st.columns(2)
    c1.metric("Usuarios", len(usuarios), border=True)
    c2.metric("De pago", f"{premium} · {round(100 * premium / len(usuarios)) if usuarios else 0} %", border=True)
    c3, c4 = st.columns(2)
    c3.metric("Nuevos esta semana", nuevos, border=True)
    c4.metric("Entrenamientos", len(sesiones), border=True)
    st.caption(f"🎁 Tarjetas regalo: {len(tarjetas)} entregadas, "
               f"{sum(1 for t in tarjetas if t.get('usada'))} usadas.")

    st.markdown("**Usuarios por plan**")
    st.bar_chart(_contar(usuarios, "plan"), horizontal=True, color="#EA580C")
    st.markdown("**Usuarios por nivel**")
    st.bar_chart(_contar(usuarios, "nivel"), horizontal=True, color="#EA580C")
    st.markdown("**Usuarios por objetivo**")
    st.bar_chart(_contar(usuarios, "objetivo"), horizontal=True, color="#EA580C")

    if sesiones:
        st.markdown("**Rutinas más hechas**")
        nombres = {r["id"]: r["nombre"] for r in datos._rutinas()}
        hechas = pd.Series([nombres.get(s["rutina_id"], s["rutina_id"]) for s in sesiones]).value_counts().head(5)
        st.bar_chart(hechas.rename("Entrenamientos").to_frame(), horizontal=True, color="#EA580C")
        valoradas = [s["valoracion"] for s in sesiones if s.get("valoracion")]
        if valoradas:
            st.markdown("**Cómo les resultan las rutinas**")
            st.bar_chart(pd.Series(valoradas).value_counts().rename("Valoraciones").to_frame(),
                         horizontal=True, color="#EA580C")
    else:
        st.caption("Todavía no hay entrenamientos guardados.")


# ---------------------------------------------------------------- 👥 usuarios
def _usuarios() -> None:
    filas = _leer("Registro de usuarios",
                  "id_usuario, Nombre, apellidos, nivel, objetivo, plan, fecha_registro", orden="id_usuario")
    c1, c2 = st.columns([2, 1])
    buscar = c1.text_input("Buscar por nombre o apellidos", key="admin_buscar")
    plan = c2.selectbox("Plan", ["Todos", "Gratuito", "De pago"], key="admin_plan")
    texto = buscar.strip().lower()
    filas = [f for f in filas
             if (not texto or texto in f"{f.get('Nombre') or ''} {f.get('apellidos') or ''}".lower())
             and (plan == "Todos" or (plan == "De pago") == _de_pago(f))]
    st.caption(f"{len(filas)} usuarios · sin correos ni contraseñas")
    columnas = {"id_usuario": "Nº", "Nombre": "Nombre", "apellidos": "Apellidos", "nivel": "Nivel",
                "objetivo": "Objetivo", "plan": "Plan", "fecha_registro": "Alta"}
    # Solo estas columnas, nunca correos ni contraseñas (aunque llegaran más datos)
    tabla = pd.DataFrame([{c: f.get(c) for c in columnas} for f in filas]).rename(columns=columnas)
    st.dataframe(tabla, hide_index=True, use_container_width=True)


# ---------------------------------------------------------------- 💪 rutinas
def _rutinas() -> None:
    rutinas = datos._rutinas()
    opciones = [NUEVA] + [f"{r['id']} · {r['nombre']}" for r in rutinas]
    elegida = st.selectbox("Rutina", opciones, key="admin_rutina")
    nueva = elegida == NUEVA
    r = {} if nueva else rutinas[opciones.index(elegida) - 1]
    clave = r.get("id", "nueva")

    with st.form(f"form_rutina_{clave}"):
        codigo = st.text_input("Código (R + peso, p. ej. R10-5)", r.get("id", ""), disabled=not nueva)
        nombre = st.text_input("Nombre (con el objetivo, p. ej. «Full Body 6 - Tonificar»)", r.get("nombre", ""))
        c1, c2 = st.columns(2)
        nivel = c1.selectbox("Nivel", datos.NIVELES,
                             index=datos.NIVELES.index(r["nivel"]) if r.get("nivel") in datos.NIVELES else 0)
        duracion = c2.number_input("Duración (min)", 5, 180, int(r.get("duracion_min") or 45), step=5)
        descripcion = st.text_area("Descripción", r.get("descripcion") or "")
        ejercicios = st.text_area("Ejercicios (uno por línea, con las series: «Sentadilla goblet 3x12»)",
                                  "\n".join(e.strip() for e in (r.get("ejercicios") or "").split(";") if e.strip()),
                                  height=180)
        guardar = st.form_submit_button("Guardar rutina", type="primary", use_container_width=True)

    if guardar:
        codigo = codigo.strip().upper()
        lista = "; ".join(l.strip() for l in ejercicios.splitlines() if l.strip())
        if not re.fullmatch(r"R\d+(-[A-Z0-9]+)?", codigo):
            st.error("El código tiene que empezar por R y el peso: R03, R10-2, R15-B…")
        elif not nombre.strip():
            st.error("La rutina necesita un nombre.")
        elif nueva and any(x["id"] == codigo for x in rutinas):
            st.error(f"Ya existe una rutina con el código {codigo}.")
        else:
            fila = {"nombre": nombre.strip(), "nivel": nivel, "duracion_min": int(duracion),
                    "descripcion": descripcion.strip(), "ejercicios": lista}
            error = (_insertar("rutinas", {"id": codigo, **fila}) if nueva
                     else _actualizar("rutinas", fila, id=codigo))
            datos._rutinas.clear()
            _resultado(error, f"Rutina {codigo} guardada. Ya se ve en la web.")


# ---------------------------------------------------------------- 📘 técnica
def _tecnica() -> None:
    filas = _leer("tecnica_ejercicios", "ejercicio, pasos, errores, imagen_url", orden="ejercicio")
    existentes = {f["ejercicio"].lower() for f in filas}
    en_rutinas = {nombre_base(e) for r in datos._rutinas()
                  for e in (r.get("ejercicios") or "").split(";") if e.strip()}
    faltan = sorted(e for e in en_rutinas if e and e.lower() not in existentes)
    if faltan:
        st.info(f"Hay {len(faltan)} ejercicios de las rutinas sin ficha de técnica.")
        if st.button(f"Añadir esos {len(faltan)} ejercicios", key="admin_tecnica_faltan"):
            _resultado(_insertar("tecnica_ejercicios", [{"ejercicio": e} for e in faltan]),
                       "Ejercicios añadidos. Ya puedes escribir su técnica.")
    if not filas:
        st.caption("Todavía no hay ejercicios.")
        return

    hechos = sum(1 for f in filas if f.get("pasos"))
    st.caption(f"✅ {hechos} de {len(filas)} ejercicios tienen la técnica escrita.")
    etiquetas = [("✅ " if f.get("pasos") else "⏳ ") + f["ejercicio"] for f in filas]
    elegido = st.selectbox("Ejercicio", etiquetas, key="admin_ejercicio")
    f = filas[etiquetas.index(elegido)]

    with st.form(f"form_tecnica_{f['ejercicio']}"):
        pasos = st.text_area("Cómo se hace (un paso por línea)", f.get("pasos") or "", height=150)
        errores = st.text_area("Errores comunes (uno por línea)", f.get("errores") or "", height=120)
        imagen = st.text_input("Enlace a una imagen o GIF (opcional)", f.get("imagen_url") or "")
        guardar = st.form_submit_button("Guardar técnica", type="primary", use_container_width=True)
    if guardar:
        error = _actualizar("tecnica_ejercicios",
                            {"pasos": pasos.strip() or None, "errores": errores.strip() or None,
                             "imagen_url": imagen.strip() or None,
                             "actualizado": datetime.now(timezone.utc).isoformat()},
                            ejercicio=f["ejercicio"])
        cuentas.usuario_actual().pop("tecnica", None)
        _resultado(error, f"Técnica de «{f['ejercicio']}» guardada.")


# ---------------------------------------------------------------- 🥗 alimentación
def _alimentacion() -> None:
    objetivo = st.selectbox("Objetivo", OBJETIVOS, key="admin_objetivo")
    fila = next(iter(_leer("alimentacion", "objetivo, titular, subtitulo, color, consejos",
                           objetivo=objetivo)), {})

    st.markdown("**Banner y consejos**")
    with st.form(f"form_banner_{objetivo}"):
        titular = st.text_input("Titular", fila.get("titular") or "")
        subtitulo = st.text_area("Subtítulo", fila.get("subtitulo") or "", height=80)
        color = st.color_picker("Color del banner", fila.get("color") or "#C2410C")
        consejos = st.text_area("Consejos (uno por línea: «Título | texto»)", fila.get("consejos") or "",
                                height=200)
        guardar = st.form_submit_button("Guardar banner y consejos", type="primary", use_container_width=True)
    if guardar:
        cambios = {"titular": titular.strip(), "subtitulo": subtitulo.strip(), "color": color,
                   "consejos": consejos.strip()}
        error = (_actualizar("alimentacion", cambios, objetivo=objetivo) if fila
                 else _insertar("alimentacion", {"objetivo": objetivo, **cambios}))
        cuentas.usuario_actual().pop("alimentacion", None)
        _resultado(error, f"Consejos de «{objetivo}» guardados.")

    st.markdown("**Menú de ejemplo**")
    dia = st.selectbox("Día", DIAS, key="admin_dia")
    tomas = _leer("menus_alimentacion", "id, orden, toma, plato, ingredientes, kcal, proteinas, hidratos, grasas",
                  orden="orden", objetivo=objetivo, dia=DIAS.index(dia) + 1)
    if not tomas:
        st.caption("Este día todavía no tiene menú.")
        return
    tabla = pd.DataFrame(tomas).set_index("id")
    editada = st.data_editor(
        tabla[["toma", "plato", "ingredientes", "kcal", "proteinas", "hidratos", "grasas"]],
        key=f"admin_menu_{objetivo}_{dia}", use_container_width=True, hide_index=True,
        disabled=["toma"],
        column_config={"ingredientes": st.column_config.TextColumn("ingredientes (separados por ;)"),
                       "proteinas": "prot. (g)", "hidratos": "hidr. (g)", "grasas": "grasas (g)"})
    st.caption(f"Total del día: {int(editada['kcal'].sum())} kcal · {int(editada['proteinas'].sum())} g prot. · "
               f"{int(editada['hidratos'].sum())} g hidr. · {int(editada['grasas'].sum())} g grasas")
    if st.button("Guardar menú del día", type="primary", use_container_width=True, key="admin_guardar_menu"):
        errores = []
        for id_toma, nueva in editada.iterrows():
            antes = tabla.loc[id_toma]
            cambios = {c: (int(nueva[c]) if c in ("kcal", "proteinas", "hidratos", "grasas") else nueva[c])
                       for c in ("plato", "ingredientes", "kcal", "proteinas", "hidratos", "grasas")
                       if nueva[c] != antes[c]}
            if cambios:
                errores.append(_actualizar("menus_alimentacion", cambios, id=int(id_toma)))
        cuentas.usuario_actual().pop("alimentacion", None)
        _resultado(next((e for e in errores if e), None), f"Menú del {dia.lower()} guardado.")


# ---------------------------------------------------------------- pantalla
def boton_menu(seccion: str, ir_a_seccion) -> None:
    """Botón del menú lateral, solo para el equipo."""
    if cuentas.es_admin():
        st.button("🛠️ Administración", key="lat_admin", use_container_width=True,
                  type="primary" if seccion == "admin" else "secondary",
                  on_click=ir_a_seccion, args=("admin",))


def mostrar() -> None:
    if not cuentas.es_admin():
        st.warning("Esta sección es solo para el equipo.")
        return
    estilos.titulo("Administración 🛠️", "Solo la ve el equipo. Los cambios se guardan en Supabase.")
    if aviso := st.session_state.pop("admin_aviso", None):
        st.success(f"✅ {aviso}")
    # Botones en vez de pestañas: así, después de guardar, sigues en la misma sección
    secciones = {"📊 Estadísticas": _estadisticas, "👥 Usuarios": _usuarios, "💪 Rutinas": _rutinas,
                 "📘 Técnica": _tecnica, "🥗 Alimentación": _alimentacion}
    elegida = st.segmented_control("Sección", list(secciones), default="📊 Estadísticas",
                                   key="admin_seccion", label_visibility="collapsed") or "📊 Estadísticas"
    st.divider()
    try:
        secciones[elegida]()
    except Exception as error:
        if type(error).__name__ in ("RerunException", "StopException"):
            raise  # st.rerun() después de guardar: no es un error
        st.error("No se han podido cargar los datos. Comprueba que se ha ejecutado "
                 "11_panel_administracion.sql en Supabase.")
