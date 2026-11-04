# Pesas que apetece enseñar · Web

Web móvil de rutinas de fuerza guiadas, vinculada a cada pesa mediante un código QR.
Proyecto de Metodologías Ágiles (G223, CUNEF).

**Tecnología:** React + Vite · React Router · Supabase (base de datos).

## Cómo funciona

- Cada pesa lleva un QR con una dirección del tipo `https://<web>/p/<código>`.
- La página `/p/<código>` busca el código en la tabla `pesas` de Supabase y muestra el peso y la rutina asociada.
- El QR solo contiene el código; la rutina asociada vive en la base de datos, así que se puede cambiar sin reimprimir.

## Pantallas (cada una en su archivo)

| Ruta | Archivo | Historia | Responsable | Estado |
|---|---|---|---|---|
| `/` | `src/pages/Home.jsx` | PVBPQAE-58 | Marta | Hecha |
| `/pesas` | `src/pages/Pesas.jsx` | PVBPQAE-58 | Marta | Hecha |
| `/p/:codigo` | `src/pages/Pesa.jsx` | PVBPQAE-58 | Marta | Hecha |
| `/admin` | `Placeholder` en `src/App.jsx` | PVBPQAE-51 | Marta | Pendiente |
| `/registro`, `/login` | `Placeholder` en `src/App.jsx` | PVBPQAE-46 | Mauro | Pendiente |
| `/onboarding` | `Placeholder` en `src/App.jsx` | PVBPQAE-27 | María Luz | Pendiente |
| `/rutina/:id` | `Placeholder` en `src/App.jsx` | PVBPQAE-25 | María Luz | Pendiente |
| Escanear QR y abrir rutina (une `/p/:codigo`, sesión, nivel y `/rutina/:id`) | por definir | PVBPQAE-47 | Elías | Pendiente |
| `/resumen` | `Placeholder` en `src/App.jsx` | PVBPQAE-31 | Javier | Pendiente |

### Cómo añadir tu pantalla

1. Crea una rama con la clave de tu historia, por ejemplo `PVBPQAE-27-onboarding`.
2. Crea tu componente en `src/pages/` (por ejemplo `Onboarding.jsx`).
3. En `src/App.jsx`, cambia el `<Placeholder ... />` de tu ruta por tu componente. No toques las demás rutas.
4. Abre un *pull request* hacia `main`.

Para leer o guardar datos usa el cliente que ya está listo:

```js
import { supabase } from '../lib/supabase.js'
const { data, error } = await supabase.from('rutinas').select('*')
```

## Ponerlo en marcha en tu ordenador

Necesitas [Node.js](https://nodejs.org) (versión LTS).

```bash
npm install
cp .env.example .env     # y rellena los dos valores (ver abajo)
npm run dev
```

### Variables de entorno

En Supabase: **Project Settings → API**. Copia la **URL del proyecto** y la clave **pública** (`anon` o `publishable`):

```
VITE_SUPABASE_URL=...
VITE_SUPABASE_KEY=...
```

> **Nunca** pongas la clave secreta (`service_role`) ni la contraseña de la base de datos en el código ni en GitHub.
> El archivo `.env` está en `.gitignore` y no se sube.

## Base de datos

Los scripts para crear las tablas (`crear_tabla_usuarios.sql`, y más adelante el de rutinas y pesas) y el CSV de usuarios sintéticos están en el repositorio, junto a este README.

## Despliegue

Pensado para Vercel (o Netlify): importar el repositorio, añadir las dos variables de entorno y desplegar.
