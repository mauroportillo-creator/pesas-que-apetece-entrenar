# Pesas que apetece entrenar · Web

Web de rutinas de fuerza hecha con **Streamlit**.
Proyecto de Metodologías Ágiles (G223, CUNEF).

## Ponerla en marcha

Necesitas Python 3.10 o superior.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abre en http://localhost:8501.

## Estructura

| Archivo | Para qué sirve |
|---|---|
| `app.py` | La aplicación |
| `inicio.md` | Texto de la página de Inicio (también se edita desde la web: «✏️ Editar descripción») |
| `datos.json` | Usuario, rutinas y productos de la tienda (datos de ejemplo por ahora) |
| `assets/` | Foto de perfil subida desde la página Usuario |
| `crear_tabla_usuarios.sql`, `crear_tablas_pesas.sql` | Scripts para crear las tablas en Supabase |
| `usuarios_sinteticos_limpio.csv` | Usuarios sintéticos para cargar en la base de datos |

## Páginas

- **Menú lateral:** Usuario (con foto de perfil), Mis Datos, Mis Rutinas.
- **Botones superiores:** Inicio, Rutinas, Tienda.

La compra de la tienda es una simulación: no hay pasarela de pago conectada.

> Nunca subas claves secretas ni contraseñas de Supabase a GitHub. Si hacen falta, van en `.streamlit/secrets.toml`, que está en `.gitignore`.
