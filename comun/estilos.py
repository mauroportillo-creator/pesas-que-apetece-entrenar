"""Estilos comunes de la web (pensada para móvil)."""
import streamlit as st

CSS = """
<style>
  #MainMenu, header [data-testid="stToolbar"], footer {visibility: hidden;}
  .block-container {padding-top: 1.2rem; padding-bottom: 3rem;}

  /* Panel lateral */
  [data-testid="stSidebar"] {background:#FFF4EC;}
  .usuario {display:flex; align-items:center; gap:.75rem; margin:.3rem 0 1rem;}
  .avatar {width:52px; height:52px; border-radius:50%; flex-shrink:0;
           background:linear-gradient(135deg,#F97316,#C2410C); color:#fff;
           display:flex; align-items:center; justify-content:center; font-weight:800; font-size:1.2rem;}
  .usuario .nombre {font-weight:700; line-height:1.2;}
  .usuario .correo {font-size:.8rem; opacity:.7; word-break:break-all;}
  .usuario .chip {display:inline-block; margin-top:.25rem; font-size:.72rem; padding:.1rem .5rem;
                  border-radius:999px; background:#FED7AA; color:#9A3412; font-weight:600;}

  /* Carrito arriba a la derecha (también en el móvil, en la misma fila que la marca) */
  [data-testid="stHorizontalBlock"]:has(.st-key-icono_carrito) {flex-wrap:nowrap; align-items:center;}
  [data-testid="stHorizontalBlock"]:has(.st-key-icono_carrito) > div {min-width:0 !important;}
  .st-key-icono_carrito {display:flex; justify-content:flex-end;}
  .st-key-icono_carrito button {position:relative; font-size:1.3rem; min-height:2.6rem; padding:0 .9rem;}
  [data-testid="stHorizontalBlock"]:has(.st-key-icono_carrito) .marca {margin-bottom:0;}

  /* Estrella para guardar rutinas: sin recuadro, grande y amarilla */
  [class*="st-key-estrella_"] button {border:none; background:transparent; box-shadow:none;
      font-size:1.7rem; line-height:1; min-height:2.6rem; padding:0; color:#F59E0B;}
  [class*="st-key-estrella_"] button:hover {background:transparent; color:#D97706; transform:scale(1.15);}
  [class*="st-key-estrella_"] button p {font-size:1.7rem;}
  /* Que la fila rutina + estrella no se parta en el móvil */
  [data-testid="stHorizontalBlock"]:has([class*="st-key-estrella_"]) {flex-wrap:nowrap;}
  [data-testid="stHorizontalBlock"]:has([class*="st-key-estrella_"]) > div:last-child {min-width:2.4rem !important; flex:0 0 2.4rem !important;}

  /* Botón grande de «Repetir el cuestionario» en Mis datos */
  .st-key-repetir_cuestionario button {min-height:3.6rem; font-size:1.08rem;}

  /* Tarjetas de producto (tienda) */
  .producto {text-align:center; position:relative;}
  .producto .foto {background:linear-gradient(180deg,#FFF7ED,#FFEDD5); border-radius:14px;
                   height:150px; display:flex; align-items:flex-end; justify-content:center;
                   padding-bottom:6px; margin-bottom:.7rem;}
  .producto .recomendada {position:absolute; top:8px; left:8px; background:#16A34A; color:#fff;
                          font-size:.7rem; font-weight:700; padding:.15rem .55rem; border-radius:999px;}
  .producto .nombre {font-weight:800; font-size:1.05rem;}
  .producto .kilos {font-weight:800; font-size:1.4rem; color:#C2410C; line-height:1.2;}
  .producto .chip-nivel {display:inline-block; margin:.3rem 0 .4rem; background:#FED7AA; color:#9A3412;
                         padding:.1rem .55rem; border-radius:999px; font-size:.72rem; font-weight:700;}
  .producto .texto {font-size:.85rem; opacity:.75; min-height:2.5rem;}
  .producto .precio {font-size:1.35rem; font-weight:800; margin:.45rem 0 .2rem; color:#1F2937;}

  .marca {display:flex; align-items:center; gap:.5rem; font-weight:800;
          font-size:1.05rem; color:#C2410C; margin-bottom:1rem;}
  .marca span {font-size:1.4rem;}

  .tarjeta-pesa {background:linear-gradient(135deg,#F97316,#C2410C); color:#fff;
                 border-radius:20px; padding:1.4rem 1.2rem; text-align:center;
                 margin-bottom:1.2rem; box-shadow:0 8px 24px rgba(194,65,12,.25);}
  .tarjeta-pesa .peso {font-size:3.4rem; font-weight:800; line-height:1;}
  .tarjeta-pesa .etiqueta {opacity:.9; font-size:.95rem; margin-top:.35rem;}
  .tarjeta-pesa .nivel {display:inline-block; margin-top:.8rem; padding:.2rem .7rem;
                        border-radius:999px; background:rgba(255,255,255,.2); font-size:.85rem;}

  .portada {background:linear-gradient(135deg,#F97316,#C2410C); color:#fff; border-radius:20px;
            padding:1.6rem 1.3rem; margin-bottom:1.2rem; box-shadow:0 8px 24px rgba(194,65,12,.25);}
  .portada-titulo {font-size:1.6rem; font-weight:800; line-height:1.2;}
  .portada-texto {opacity:.92; margin-top:.5rem;}
  .ventaja {display:flex; gap:.8rem; align-items:flex-start; padding:.7rem .2rem;
            border-bottom:1px solid #F3E8DE;}
  .ventaja-icono {font-size:1.5rem; line-height:1; width:2rem; flex-shrink:0; text-align:center;}
  .ventaja-titulo {font-weight:700;}
  .ventaja-texto {font-size:.9rem; opacity:.75;}

  .titulo {font-size:1.5rem; font-weight:800; margin:.2rem 0 .3rem;}
  .subtitulo {opacity:.75; margin-bottom:1rem;}
  .pie {text-align:center; opacity:.6; font-size:.8rem; margin-top:2rem;}

  .stButton > button, .stFormSubmitButton > button {border-radius:12px; min-height:3rem; font-weight:600;}
</style>
"""


def aplicar(con_panel: bool = False) -> None:
    """con_panel=True en la pantalla principal (panel lateral y más ancho)."""
    st.markdown(CSS, unsafe_allow_html=True)
    if con_panel:
        extra = ".block-container {max-width: 820px;}"
    else:
        extra = ('.block-container {max-width: 460px;} '
                 '[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {display:none;}')
    st.markdown(f"<style>{extra}</style>", unsafe_allow_html=True)


def contador_carrito(unidades: int) -> None:
    """Círculo rojo con el número de productos, encima del icono del carrito."""
    numero = "9+" if unidades > 9 else str(unidades)
    st.markdown(
        "<style>"
        f'.st-key-icono_carrito button::after {{content:"{numero}"; position:absolute; top:-8px; right:-8px;'
        " min-width:20px; height:20px; padding:0 5px; border-radius:999px; background:#DC2626;"
        " color:#fff; font-size:.72rem; font-weight:700; line-height:20px; text-align:center;"
        " box-shadow:0 0 0 2px #fff;}"
        "</style>",
        unsafe_allow_html=True,
    )


# Colores mate de las mancuernas de neopreno: (claro, medio, oscuro, fondo de la foto)
COLORES_MANCUERNA = {
    3: ("#A9D6D1", "#72B5AE", "#4A8C86", "#F1F8F7"),    # turquesa
    5: ("#BEDDB2", "#86B874", "#5B8A4B", "#F3F8F1"),    # verde
    10: ("#B7CDEA", "#7A9FD2", "#4D72A8", "#F1F5FB"),   # azul
    15: ("#CDC3E8", "#9C8BD0", "#6A589E", "#F5F3FB"),   # morado
}


def color_mancuerna(peso_kg: int) -> str:
    """Color principal (oscuro) de la mancuerna, para textos a juego."""
    return COLORES_MANCUERNA.get(peso_kg, ("", "", "#C2410C", ""))[2]


def fondo_mancuerna(peso_kg: int) -> str:
    """Color suave para el fondo de la foto, a juego con la mancuerna."""
    return COLORES_MANCUERNA.get(peso_kg, ("", "", "", "#FFF7ED"))[3]


def _hexagono(cx: float, cy: float, alto: float) -> str:
    """Puntos de un hexágono (cabeza de la mancuerna) con las puntas arriba y abajo."""
    w = alto * 0.82
    puntos = [(cx, cy - alto), (cx + w, cy - alto / 2), (cx + w, cy + alto / 2),
              (cx, cy + alto), (cx - w, cy + alto / 2), (cx - w, cy - alto / 2)]
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in puntos)


def _mancuerna(cx: float, cy: float, alto: float, color: str, sombra: str, mango: str,
               texto: str | None) -> str:
    """Mancuerna tumbada: mango con agarre y topes, y dos cabezas hexagonales con grosor y bisel."""
    separacion = 30 + alto
    izq, der = cx - separacion, cx + separacion
    w = alto * 0.82
    redondeo = f'stroke-width="{alto * 0.35:.1f}" stroke-linejoin="round"'
    alto_mango = alto * 0.6
    partes = [
        # Mango: color base, brillo mate arriba y líneas del agarre en el centro
        f'<rect x="{izq:.1f}" y="{cy - alto_mango / 2:.1f}" width="{der - izq:.1f}" height="{alto_mango:.1f}" '
        f'rx="{alto_mango / 2:.1f}" fill="{mango}"/>',
        f'<rect x="{izq:.1f}" y="{cy - alto_mango / 2 + 1:.1f}" width="{der - izq:.1f}" '
        f'height="{alto_mango * 0.3:.1f}" rx="{alto_mango * 0.15:.1f}" fill="#fff" opacity=".22"/>',
    ]
    for i in range(-5, 6):
        x = cx + i * 3.2
        partes.append(f'<line x1="{x:.1f}" y1="{cy - alto_mango / 2 + 1.5:.1f}" x2="{x:.1f}" '
                      f'y2="{cy + alto_mango / 2 - 1.5:.1f}" stroke="#000" stroke-opacity=".14" stroke-width="1"/>')
    for x in (izq + w + 3, der - w - 3):   # topes entre la cabeza y el mango
        partes.append(f'<rect x="{x - 3:.1f}" y="{cy - alto * 0.42:.1f}" width="6" height="{alto * 0.84:.1f}" '
                      f'rx="2" fill="{sombra}"/>')
    for x in (izq, der):
        partes.append(  # grosor (la cara de atrás asoma un poco), cara y bisel
            f'<polygon points="{_hexagono(x + 3.5, cy + 2.5, alto)}" fill="{sombra}" stroke="{sombra}" {redondeo}/>'
            f'<polygon points="{_hexagono(x, cy, alto)}" fill="{color}" stroke="{color}" {redondeo}/>'
            f'<polygon points="{_hexagono(x, cy, alto * 0.74)}" fill="none" stroke="#fff" '
            f'stroke-opacity=".22" stroke-width="1.4" stroke-linejoin="round"/>')
    if texto:
        partes.append(
            f'<text x="{izq:.1f}" y="{cy + 1:.1f}" text-anchor="middle" dominant-baseline="middle" '
            f'font-family="Source Sans Pro, Arial, sans-serif" font-weight="700" '
            f'font-size="{alto * (0.95 if len(texto) == 1 else 0.78):.1f}" fill="#fff">{texto}</text>'
            f'<text x="{der:.1f}" y="{cy + 1:.1f}" text-anchor="middle" dominant-baseline="middle" '
            f'font-family="Source Sans Pro, Arial, sans-serif" font-weight="700" '
            f'font-size="{alto * 0.55:.1f}" letter-spacing=".5" fill="#fff">KG</text>')
    return "".join(partes)


def dibujo_mancuernas(peso_kg: int, ancho: int = 200) -> str:
    """Dibujo de una pareja de mancuernas hexagonales de neopreno con el peso escrito.
    Cada peso tiene su color y las cabezas son más grandes cuanto más pesa."""
    claro, medio, oscuro, _ = COLORES_MANCUERNA.get(peso_kg, ("#B7CDEA", "#7A9FD2", "#4D72A8", ""))
    alto = {3: 18, 5: 19.5, 10: 21, 15: 22.5}.get(peso_kg, 19.5)
    return (f'<svg viewBox="0 0 205 132" width="{ancho}" role="img" '
            f'aria-label="Pareja de mancuernas de {peso_kg} kg" xmlns="http://www.w3.org/2000/svg">'
            f'<ellipse cx="102" cy="{94 + alto + 10:.1f}" rx="80" ry="5" fill="{oscuro}" opacity=".14"/>'
            f'{_mancuerna(112, 46, alto * 0.9, claro, medio, claro, None)}'
            f'{_mancuerna(96, 90, alto, medio, oscuro, oscuro, str(peso_kg))}'
            f'</svg>')


def iniciales(nombre: str, apellidos: str = "") -> str:
    partes = (nombre.split()[:1] + apellidos.split()[:1])
    return "".join(p[0] for p in partes).upper() or "?"


def cabecera() -> None:
    st.markdown('<div class="marca"><span>🏋️</span> Pesas que apetece enseñar</div>',
                unsafe_allow_html=True)


def tarjeta_pesa(peso_kg: int, nivel: str, etiqueta: str = "Has escaneado tu pesa") -> None:
    st.markdown(
        f'<div class="tarjeta-pesa"><div class="peso">{peso_kg} kg</div>'
        f'<div class="etiqueta">{etiqueta}</div>'
        f'<div class="nivel">Nivel {nivel.lower()}</div></div>',
        unsafe_allow_html=True,
    )


def titulo(texto: str, subtitulo: str | None = None) -> None:
    st.markdown(f'<div class="titulo">{texto}</div>', unsafe_allow_html=True)
    if subtitulo:
        st.markdown(f'<div class="subtitulo">{subtitulo}</div>', unsafe_allow_html=True)
