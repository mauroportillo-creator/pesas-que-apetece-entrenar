-- Pesas que apetece enseñar · Sesiones de entrenamiento (PVBPQAE-31, resumen y valoración)
-- Pegar en Supabase: SQL Editor > New query > Run   (se puede ejecutar más de una vez)
-- Ejecutar después de 1_crear_tabla_rutinas.sql.
--
-- Cada vez que alguien finaliza una rutina se guarda una fila con su resumen
-- y, si la da, su valoración (Fácil, Adecuada o Dura).

create table if not exists sesiones_entrenamiento (
  id                     bigint generated always as identity primary key,
  auth_id                uuid not null default auth.uid() references auth.users(id) on delete cascade,
  rutina_id              text not null references rutinas(id) on delete cascade,
  inicio                 timestamptz not null,
  fin                    timestamptz not null,
  estado                 text not null check (estado in ('Completa', 'Parcial')),
  ejercicios_completados integer not null,
  ejercicios_total       integer not null,
  series_hechas          integer not null,
  series_total           integer not null,
  duracion_min           integer not null,
  valoracion             text check (valoracion in ('Fácil', 'Adecuada', 'Dura'))  -- vacía si la salta
);

-- Seguridad: cada persona solo ve, guarda y valora SUS sesiones (RLS)
alter table sesiones_entrenamiento enable row level security;

drop policy if exists "ver mis sesiones" on sesiones_entrenamiento;
create policy "ver mis sesiones" on sesiones_entrenamiento
  for select to authenticated using (auth_id = auth.uid());

drop policy if exists "guardar mis sesiones" on sesiones_entrenamiento;
create policy "guardar mis sesiones" on sesiones_entrenamiento
  for insert to authenticated with check (auth_id = auth.uid());

drop policy if exists "valorar mis sesiones" on sesiones_entrenamiento;
create policy "valorar mis sesiones" on sesiones_entrenamiento
  for update to authenticated using (auth_id = auth.uid()) with check (auth_id = auth.uid());

-- Si se borra la cuenta de una persona, sus sesiones se borran solas (on delete cascade).
