-- Pesas que apetece enseñar · Técnica explicada de cada ejercicio (PVBPQAE-12)
-- Pegar en Supabase: SQL Editor > New query > Run   (se puede ejecutar más de una vez)
-- Ejecutar DESPUÉS de 8_suscripcion_premium.sql.
--
-- Qué hace:
--   1. Crea la tabla «tecnica_ejercicios»: una fila por ejercicio con sus pasos y sus errores comunes.
--   2. La rellena con todos los ejercicios que ya hay en las rutinas, con el texto vacío.
--      Solo hay que escribir «pasos» y «errores» (hoy en Table Editor; más adelante, desde el
--      panel de administración, PVBPQAE-95).
--   3. Seguridad: solo las personas Premium pueden leerla (la técnica es contenido Premium).
--
-- El nombre del ejercicio se guarda sin las series: «Sentadilla goblet 3x15» → «Sentadilla goblet».
-- Así una misma explicación sirve para todas las rutinas que tienen ese ejercicio.


-- 1. Tabla ------------------------------------------------------------------------
create table if not exists tecnica_ejercicios (
  ejercicio    text primary key,          -- p. ej. «Sentadilla goblet»
  pasos        text,                      -- cómo se hace, un paso por línea
  errores      text,                      -- errores comunes, uno por línea
  imagen_url   text,                      -- opcional: enlace a una imagen o GIF
  actualizado  timestamptz not null default now()
);


-- 2. Rellenar con los ejercicios de las rutinas (sin repetir y sin las series) -------
insert into tecnica_ejercicios (ejercicio)
select distinct regexp_replace(trim(e), '[[:space:]]+[0-9].*$', '')
from rutinas, regexp_split_to_table(coalesce(ejercicios, ''), ';') as e
where trim(e) <> ''
on conflict (ejercicio) do nothing;


-- 3. Seguridad: solo Premium la puede leer (RLS) -----------------------------------
-- Nadie puede cambiarla desde la web todavía: el equipo la rellena en Supabase
-- (Table Editor) hasta que exista el panel de administración.
alter table tecnica_ejercicios enable row level security;

drop policy if exists "leer la tecnica si soy premium" on tecnica_ejercicios;
create policy "leer la tecnica si soy premium" on tecnica_ejercicios
  for select to authenticated
  using (exists (select 1 from "Registro de usuarios" r
                 where r.auth_id = auth.uid() and r.plan = 'Premium'));

-- Si más adelante se añade un ejercicio nuevo a una rutina, se puede volver a ejecutar
-- este script: añade los ejercicios que falten y no toca los que ya están escritos.
