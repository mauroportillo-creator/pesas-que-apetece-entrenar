-- Pesas que apetece enseñar · «Mis rutinas»: rutinas que cada persona guarda con la estrella
-- Pegar en Supabase: SQL Editor > New query > Run   (se puede ejecutar más de una vez)
-- Ejecutar después de 1_crear_tabla_rutinas.sql y de importar rutinas.csv.

create table if not exists rutinas_guardadas (
  auth_id    uuid not null default auth.uid() references auth.users(id) on delete cascade,
  rutina_id  text not null references rutinas(id) on delete cascade,
  fecha      date not null default current_date,
  primary key (auth_id, rutina_id)          -- la misma rutina no se guarda dos veces
);

-- Seguridad: cada persona solo ve, guarda y quita SUS rutinas (RLS)
alter table rutinas_guardadas enable row level security;

drop policy if exists "ver mis rutinas guardadas" on rutinas_guardadas;
create policy "ver mis rutinas guardadas" on rutinas_guardadas
  for select to authenticated using (auth_id = auth.uid());

drop policy if exists "guardar mis rutinas" on rutinas_guardadas;
create policy "guardar mis rutinas" on rutinas_guardadas
  for insert to authenticated with check (auth_id = auth.uid());

drop policy if exists "quitar mis rutinas" on rutinas_guardadas;
create policy "quitar mis rutinas" on rutinas_guardadas
  for delete to authenticated using (auth_id = auth.uid());

-- Si se borra la cuenta de una persona, sus rutinas guardadas se borran solas (on delete cascade).
