"""Genera los QR de las pesas (PVBPQAE-51).

Crea un PNG por pesa (QR + peso + código) y una hoja A4 en PDF con todos para imprimir.
Cada QR lleva solo la dirección de la web con el código de la pesa (?pesa=CÓDIGO).

Uso:
    pip install "qrcode[pil]"
    python generar_qr.py "carpeta donde guardarlos"

Si cambia la dirección de la web o se añade una pesa, se cambian WEB y PESAS.
"""
import sys
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont

WEB = "https://pesas-que-apetece-ensenar.streamlit.app/?pesa="
PESAS = [("n4v8c2", 3), ("h6j3x9", 5), ("r2t7w5", 10), ("f9d4s1", 15)]
NARANJA = (217, 84, 15)
salida = Path(sys.argv[1])
salida.mkdir(parents=True, exist_ok=True)


def fuente(tam, negrita=False):
    for nombre in (("arialbd.ttf" if negrita else "arial.ttf"), "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(nombre, tam)
        except OSError:
            pass
    return ImageFont.load_default()


def tarjeta(codigo, kg):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=20, border=2)
    qr.add_data(WEB + codigo)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    w = img_qr.width
    alto_texto = 260
    lienzo = Image.new("RGB", (w, w + alto_texto), "white")
    lienzo.paste(img_qr, (0, 0))
    d = ImageDraw.Draw(lienzo)
    for texto, f, y, color in (
        (f"{kg} kg", fuente(110, True), w + 10, NARANJA),
        ("Pesas que apetece enseñar", fuente(46), w + 140, (40, 40, 40)),
        (f"código: {codigo}", fuente(34), w + 200, (120, 120, 120)),
    ):
        tw = d.textlength(texto, font=f)
        d.text(((w - tw) / 2, y), texto, font=f, fill=color)
    return lienzo


tarjetas = []
for codigo, kg in PESAS:
    t = tarjeta(codigo, kg)
    t.save(salida / f"QR pesa {kg} kg.png")
    tarjetas.append(t)

# Hoja A4 (300 ppp) con las 4 tarjetas en 2x2
A4 = (2480, 3508)
hoja = Image.new("RGB", A4, "white")
celda_w, celda_h = A4[0] // 2, A4[1] // 2
for i, t in enumerate(tarjetas):
    escala = min((celda_w - 200) / t.width, (celda_h - 200) / t.height)
    t2 = t.resize((int(t.width * escala), int(t.height * escala)), Image.LANCZOS)
    x = (i % 2) * celda_w + (celda_w - t2.width) // 2
    y = (i // 2) * celda_h + (celda_h - t2.height) // 2
    hoja.paste(t2, (x, y))
hoja.save(salida / "QR - las 4 pesas (A4).pdf", resolution=300)
print("hecho:", sorted(p.name for p in salida.iterdir()))
