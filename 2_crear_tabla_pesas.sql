-- Pesas que apetece enseñar · Tabla de pesas
-- Pegar en Supabase: SQL Editor > New query > Run
-- Ejecutar DESPUÉS de 1_crear_tabla_rutinas.sql.
-- Datos: importar pesas.csv (Table Editor > pesas > Insert > Import data from CSV)
--
-- Cada pesa física (3, 5, 10 y 15 kg) tiene un código único, el que lleva su QR,
-- y una rutina asociada. La rutina se puede cambiar sin reimprimir el QR.

create table if not exists pesas (
  codigo     text primary key,
  peso_kg    integer not null,
  rutina_id  text references rutinas(id)
);

-- Seguridad: la web puede LEER las pesas, pero no modificarlas
alter table pesas enable row level security;

drop policy if exists "lectura publica pesas" on pesas;
create policy "lectura publica pesas" on pesas for select using (true);
