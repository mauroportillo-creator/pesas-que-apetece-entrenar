"""Carrito de la compra (historia por asignar, junto con la tienda).

BORRADOR: las formas de pago solo se muestran. No se cobra nada.
"""
import streamlit as st

from comun import datos, estilos


def _carrito() -> dict:
    return st.session_state.setdefault("carrito", {})


def anadir(peso_kg: int) -> None:
    _carrito()[peso_kg] = _carrito().get(peso_kg, 0) + 1
    st.toast(f"Mancuernas de {peso_kg} kg añadidas al carrito 🛒")


def cambiar_cantidad(peso_kg: int, cambio: int) -> None:
    nueva = _carrito().get(peso_kg, 0) + cambio
    if nueva <= 0:
        _carrito().pop(peso_kg, None)
    else:
        _carrito()[peso_kg] = nueva


def quitar(peso_kg: int) -> None:
    _carrito().pop(peso_kg, None)


def total_unidades() -> int:
    return sum(_carrito().values())


def _formas_de_pago() -> None:
    st.subheader("Forma de pago")
    st.caption("🛠️ Borrador: las formas de pago solo se muestran. No se realiza ningún cobro.")
    tarjeta, bizum, regalo = st.tabs(["💳 Tarjeta", "📱 Bizum", "🎁 Tarjeta regalo"])
    with tarjeta:
        st.text_input("Titular de la tarjeta", placeholder="Nombre y apellidos", disabled=True)
        st.text_input("Número de tarjeta", placeholder="•••• •••• •••• ••••", disabled=True)
        c1, c2 = st.columns(2)
        c1.text_input("Caducidad", placeholder="MM/AA", disabled=True)
        c2.text_input("CVV", placeholder="•••", disabled=True)
    with bizum:
        st.text_input("Teléfono asociado a Bizum", placeholder="6•• ••• •••", disabled=True)
        st.caption("Recibirías una notificación en tu app del banco para confirmar el pago.")
    with regalo:
        st.text_input("Código de la tarjeta regalo", placeholder="XXXX-XXXX-XXXX", disabled=True)
        st.caption("El importe se descontaría del saldo de tu tarjeta regalo.")
    st.button("Pagar", type="primary", use_container_width=True, disabled=True,
              help="Desactivado: esto es un borrador.")


def mostrar(ir_a_seccion) -> None:
    estilos.titulo("🛒 Tu carrito")
    carrito = _carrito()
    if not carrito:
        st.info("Tu carrito está vacío.")
        st.button("Ir a la tienda", type="primary", on_click=ir_a_seccion, args=("tienda",))
        return

    productos = {p["peso_kg"]: p for p in datos.PRODUCTOS}
    total = 0.0
    for peso, cantidad in sorted(carrito.items()):
        p = productos[peso]
        subtotal = p["precio"] * cantidad
        total += subtotal
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 1], vertical_alignment="center")
            c1.markdown(f"**Pareja de mancuernas de {peso} kg**  \n{p['precio']:.2f} € · {p['nivel']}")
            menos, num, mas = c2.columns(3, vertical_alignment="center")
            menos.button("−", key=f"menos_{peso}", on_click=cambiar_cantidad, args=(peso, -1))
            num.markdown(f"<div style='text-align:center;font-weight:700'>{cantidad}</div>",
                         unsafe_allow_html=True)
            mas.button("+", key=f"mas_{peso}", on_click=cambiar_cantidad, args=(peso, 1))
            c3.button("🗑️", key=f"quitar_{peso}", on_click=quitar, args=(peso,), help="Quitar")
            st.caption(f"Subtotal: {subtotal:.2f} €")

    st.markdown(f"### Total: {total:.2f} €")
    st.button("← Seguir comprando", type="tertiary", on_click=ir_a_seccion, args=("tienda",))
    st.divider()
    _formas_de_pago()
