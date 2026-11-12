-- Pesas que apetece enseñar · Conectar la tabla de usuarios con las cuentas de Supabase
-- Pegar en Supabase: SQL Editor > New query > Run   (se puede ejecutar más de una vez)

-- 1. Enlazar cada perfil con su cuenta de Supabase Authentication
--    (los 150 usuarios sintéticos no tienen cuenta, así que se quedan vacíos)
alter table "Registro de usuarios"
  add column if not exists auth_id uuid unique references auth.users(id) on delete cascade;

-- 2. Número automático para los usuarios nuevos: U0151, U0152…
create sequence if not exists registro_usuarios_seq start 151;
alter table "Registro de usuarios"
  alter column id_usuario set default 'U' || lpad(nextval('registro_usuarios_seq')::text, 4, '0');

-- 3. Cuando alguien se registra en la web, se crea solo su perfil con los datos del formulario
create or replace function public.crear_perfil_usuario()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into "Registro de usuarios"
    (auth_id, "Nombre", apellidos, correo, edad, genero, peso_pesa_kg,
     fecha_registro, plan, unido_a_reto, rutinas_completadas, racha_semanas,
     primera_rutina_en_7_dias, activa_ultimos_30_dias)
  values
    (new.id,
     new.raw_user_meta_data ->> 'nombre',
     new.raw_user_meta_data ->> 'apellidos',
     new.email,
     (new.raw_user_meta_data ->> 'edad')::bigint,
     new.raw_user_meta_data ->> 'genero',
     (new.raw_user_meta_data ->> 'peso_pesa_kg')::bigint,
     current_date, 'Gratuito', false, 0, 0, false, false);
  return new;
end;
$$;

drop trigger if exists al_crear_cuenta on auth.users;
create trigger al_crear_cuenta
  after insert on auth.users
  for each row execute function public.crear_perfil_usuario();

-- 4. Permisos: cada persona solo puede ver y cambiar SU perfil (RLS)
drop policy if exists "ver mi perfil" on "Registro de usuarios";
create policy "ver mi perfil" on "Registro de usuarios"
  for select to authenticated using (auth_id = auth.uid());

drop policy if exists "editar mi perfil" on "Registro de usuarios";
create policy "editar mi perfil" on "Registro de usuarios"
  for update to authenticated
  using (auth_id = auth.uid())
  with check (auth_id = auth.uid());

-- La contraseña ya NO se guarda en esta tabla: la guarda Supabase Authentication.
-- La columna "contraseña" se queda solo para los 150 usuarios sintéticos.
