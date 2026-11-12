# Pesas que apetece enseñar · Web

Web de rutinas de fuerza guiadas, hecha con **Streamlit** y conectada a **Supabase**.
Proyecto de Metodologías Ágiles (G223, CUNEF).

Cada pesa lleva un QR que abre la web en la página de esa pesa (`.../?pesa=<código>`).
Si se entra sin QR, se ve la página general de inicio, con acceso a registro e inicio de sesión.

## Ponerla en marcha

Necesitas Python 3.10 o superior.

```bash
pip install -r requirements.txt
```

Copia `.streamlit/secrets.example.toml` como `.streamlit/secrets.toml` y rellena la dirección
y la clave **pública** de Supabase (pídeselas al equipo). Ese archivo **no se sube a GitHub**.

```bash
python -m streamlit run app.py
```

Se abre en http://localhost:8501.

## Estructura (un archivo por historia)

| Archivo | Qué es | Historia |
|---|---|---|
| `app.py`, `comun/` | Esqueleto: navegación, estilos, datos y conexión con Supabase | PVBPQAE-58 (Marta) |
| `paginas/inicio.py` | Página general de inicio (sin QR) | PVBPQAE-58 (Marta) |
| `paginas/pesa.py` | Página de cada pesa y aviso de nivel | PVBPQAE-58 (Marta) |
| `paginas/principal.py` | Pantalla principal: panel lateral, Inicio y Rutinas | PVBPQAE-58 (Marta) |
| `paginas/cuestionario.py` | Cuestionario de nivel y objetivo | PVBPQAE-27 (María Luz) |
| `paginas/rutina.py` | Cómo se muestra una rutina | PVBPQAE-25 (María Luz) |
| `paginas/registro_login.py`, `paginas/mis_datos.py`, `comun/autenticacion.py` | Registro, inicio de sesión, recuperar contraseña y Mis datos | PVBPQAE-46 (Mauro) — **provisional** |
| `paginas/tienda.py`, `paginas/carrito.py`, `paginas/mis_rutinas.py` | Tienda, carrito y Mis rutinas | Por asignar |

## Base de datos (Supabase)

Para montarla desde cero, ejecuta los SQL en orden en **SQL Editor** e importa los CSV:

1. `1_crear_tabla_rutinas.sql` + `rutinas.csv`
2. `2_crear_tabla_pesas.sql` + `pesas.csv`
3. `3_crear_tabla_usuarios.sql` + `usuarios.csv`
4. `4_conectar_usuarios_con_cuentas.sql` (con la parte de registro)
5. `5_crear_tabla_rutinas_guardadas.sql`

La configuración del correo (cuenta de envío y plantillas con código) se hace en el panel
de Supabase y está documentada en Confluence.
