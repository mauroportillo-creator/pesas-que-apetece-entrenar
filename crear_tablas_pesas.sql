-- Pesas que apetece enseñar · Tablas de rutinas y pesas (PVBPQAE-58 y PVBPQAE-51)
-- Pegar en Supabase: SQL Editor > New query > Run
--
-- Las rutinas están VACÍAS A PROPÓSITO: solo tienen un nombre provisional.
-- El contenido (ejercicios, series, repeticiones) lo define quien haga PVBPQAE-25.

create table if not exists rutinas (
  id      text primary key,
  nombre  text not null,
  nivel   text not null check (nivel in ('Principiante','Intermedio','Avanzado'))
);

-- Cada pesa física tiene un código único (el que lleva el QR) y una rutina asociada
create table if not exists pesas (
  codigo     text primary key,
  peso_kg    int  not null,
  rutina_id  text references rutinas(id)
);

-- Una rutina provisional por cada pesa (el nombre y el nivel se pueden cambiar luego)
insert into rutinas (id, nombre, nivel) values
  ('R03', 'Rutina de 3 kg',  'Principiante'),
  ('R05', 'Rutina de 5 kg',  'Principiante'),
  ('R10', 'Rutina de 10 kg', 'Intermedio'),
  ('R15', 'Rutina de 15 kg', 'Avanzado')
on conflict do nothing;

-- Pesas de 3, 5, 10 y 15 kg, con códigos de prueba
insert into pesas (codigo, peso_kg, rutina_id) values
  ('n4v8c2',  3, 'R03'),
  ('h6j3x9',  5, 'R05'),
  ('r2t7w5', 10, 'R10'),
  ('f9d4s1', 15, 'R15')
on conflict do nothing;

-- Seguridad: la web puede LEER rutinas y pesas
alter table rutinas enable row level security;
alter table pesas   enable row level security;

drop policy if exists "lectura publica rutinas" on rutinas;
create policy "lectura publica rutinas" on rutinas for select using (true);

drop policy if exists "lectura publica pesas" on pesas;
create policy "lectura publica pesas" on pesas for select using (true);
