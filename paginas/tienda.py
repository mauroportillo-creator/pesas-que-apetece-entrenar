"""Tienda de pesas (historia por asignar).

PROVISIONAL: precios de ejemplo. Los productos se añaden al carrito (paginas/carrito.py).
Las imágenes son dibujos hechos con código (comun/estilos.py → dibujo_mancuernas).
"""
import streamlit as st

from comun import cuentas, datos, estilos
from paginas import carrito


def mostrar(ir_a_seccion) -> None:
    estilos.titulo("Tienda", "Elige las mancuernas que mejor se adaptan a ti. Se venden por parejas.")
    nivel_usuario = (cuentas.usuario_actual() or {}).get("nivel")

    columnas = st.columns(2)
    for i, p in enumerate(datos.PRODUCTOS):
        with columnas[i % 2], st.container(border=True):
            etiqueta = ('<div class="recomendada">✓ Para tu nivel</div>'
                        if p["nivel"] == nivel_usuario else "")
            st.markdown(
                f'<div class="producto">{etiqueta}'
                f'<div class="foto" style="background:{estilos.fondo_mancuerna(p["peso_kg"])}">'
                f'{estilos.dibujo_mancuernas(p["peso_kg"])}</div>'
                f'<div class="nombre">Pareja de mancuernas</div><div class="kilos" style="color:{estilos.color_mancuerna(p["peso_kg"])}">'
                f'{p["peso_kg"]} kg cada una</div>'
                f'<span class="chip-nivel">{p["nivel"]}</span>'
                f'<div class="texto">{p["texto"]}</div>'
                f'<div class="precio">{p["precio"]:.2f} €</div></div>',
                unsafe_allow_html=True,
            )
            st.button("🛒 Añadir al carrito", key=f"comprar_{p['peso_kg']}", use_container_width=True,
                      type="primary", on_click=carrito.anadir, args=(p["peso_kg"],))

    unidades = carrito.total_unidades()
    if unidades:
        st.button(f"Ver carrito ({unidades}) →", use_container_width=True,
                  on_click=ir_a_seccion, args=("carrito",))
