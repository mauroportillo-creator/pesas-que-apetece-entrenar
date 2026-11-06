-- Pesas que apetece enseñar · Registro de usuarios (sintéticos)
-- Pegar en Supabase: SQL Editor > New query > Run
-- Datos: importar usuarios.csv (Table Editor > Registro de usuarios > Insert > Import data from CSV)
--
-- peso_pesa_kg depende del nivel:
--   Principiante -> 3 o 5 kg · Intermedio -> 10 kg · Avanzado -> 15 kg
--
-- Contraseñas: se guardan CIFRADAS (hash bcrypt), nunca en texto plano.
-- Todos los usuarios sintéticos tienen la contraseña de prueba: prueba123

create table if not exists "Registro de usuarios" (
  id_usuario                text primary key,
  "Nombre"                  text,
  apellidos                 text,
  correo                    text unique,
  "contraseña"              text,
  fecha_registro            date,
  edad                      bigint,
  genero                    text,
  peso_pesa_kg              bigint,
  nivel                     text,
  objetivo                  text,
  fecha_primera_rutina      date,
  primera_rutina_en_7_dias  boolean,
  rutinas_completadas       bigint,
  fecha_ultima_actividad    date,
  activa_ultimos_30_dias    boolean,
  racha_semanas             bigint,
  plan                      text,
  fecha_suscripcion         date,
  unido_a_reto              boolean
);

-- Seguridad: tabla privada (nadie la lee desde la web sin permiso)
alter table "Registro de usuarios" enable row level security;

-- ---------------------------------------------------------------
-- Ejemplos útiles (no se ejecutan solos: copiar y adaptar)
-- ---------------------------------------------------------------

-- Poner o cambiar una contraseña (siempre cifrada):
-- update "Registro de usuarios"
-- set "contraseña" = extensions.crypt('NuevaContraseña', extensions.gen_salt('bf'))
-- where correo = 'correo@del.usuario';

-- Comprobar un login (devuelve una fila si la contraseña es correcta):
-- select id_usuario, "Nombre" from "Registro de usuarios"
-- where correo = 'correo@del.usuario'
--   and "contraseña" = extensions.crypt('contraseña_escrita', "contraseña");
