-- Pesas que apetece enseñar · Tabla de rutinas
-- Pegar en Supabase: SQL Editor > New query > Run
-- Ejecutar ANTES que 2_crear_tabla_pesas.sql (las pesas apuntan a las rutinas).
-- Datos: importar rutinas.csv (Table Editor > rutinas > Insert > Import data from CSV)

create table if not exists rutinas (
  id      text primary key,
  nombre  text not null,
  nivel   text not null check (nivel in ('Principiante', 'Intermedio', 'Avanzado')),
  -- Contenido de la rutina (vacío hasta que se definan las rutinas de cada peso)
  duracion_min  integer,  -- duración aproximada en minutos
  descripcion   text,     -- breve explicación de la rutina
  ejercicios    text      -- lista de ejercicios, p. ej.: Sentadilla 3x12; Press de hombro 3x10
);

-- Si la tabla ya existía sin las columnas de contenido, esto las añade:
alter table rutinas
  add column if not exists duracion_min integer,
  add column if not exists descripcion  text,
  add column if not exists ejercicios   text;

-- Seguridad: la web puede LEER las rutinas, pero no modificarlas
alter table rutinas enable row level security;

drop policy if exists "lectura publica rutinas" on rutinas;
create policy "lectura publica rutinas" on rutinas for select using (true);
