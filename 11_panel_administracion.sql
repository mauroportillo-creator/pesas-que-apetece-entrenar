-- Pesas que apetece enseñar · Panel de administración (PVBPQAE-95, Marta)
-- Pegar en Supabase: SQL Editor > New query > Run   (se puede ejecutar más de una vez)
-- Ejecutar DESPUÉS de 8_suscripcion_premium.sql, 9_crear_tabla_tecnica.sql y
-- 10_crear_tabla_alimentacion.sql.
--
-- Qué hace:
--   1. Crea la tabla «administradores»: las cuentas del equipo que pueden entrar en el panel.
--   2. Crea la función soy_admin(): dice si la persona que ha iniciado sesión es del equipo.
--   3. Da permisos SOLO a los administradores para:
--      · ver todos los usuarios, entrenamientos y tarjetas (para las estadísticas),
--      · añadir y cambiar rutinas, técnica de los ejercicios y alimentación.
--   El resto de personas sigue igual: solo ve lo suyo.
--
-- Nunca se usa la clave secreta de Supabase (service_role) en la web: todo va con estas reglas.


-- 1. Administradores ------------------------------------------------------------------
create table if not exists administradores (
  auth_id  uuid primary key references auth.users(id) on delete cascade,
  nombre   text not null,
  desde    date not null default current_date
);

alter table administradores enable row level security;

-- Cada persona solo puede ver si ella misma está en la tabla. Nadie puede añadirse desde la web.
drop policy if exists "ver si soy admin" on administradores;
create policy "ver si soy admin" on administradores
  for select to authenticated using (auth_id = auth.uid());


-- 2. ¿Soy administradora? ---------------------------------------------------------------
create or replace function public.soy_admin()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (select 1 from administradores where auth_id = auth.uid());
$$;

revoke all on function public.soy_admin() from public, anon;
grant execute on function public.soy_admin() to authenticated;


-- 3. Permisos de los administradores ----------------------------------------------------

-- Usuarios (solo leer: para la lista y las estadísticas). La web nunca muestra contraseñas.
drop policy if exists "admin ve todos los perfiles" on "Registro de usuarios";
create policy "admin ve todos los perfiles" on "Registro de usuarios"
  for select to authenticated using (public.soy_admin());

-- Entrenamientos y tarjetas regalo (solo leer: para las estadísticas)
drop policy if exists "admin ve todas las sesiones" on sesiones_entrenamiento;
create policy "admin ve todas las sesiones" on sesiones_entrenamiento
  for select to authenticated using (public.soy_admin());

drop policy if exists "admin ve todas las tarjetas" on tarjetas_regalo;
create policy "admin ve todas las tarjetas" on tarjetas_regalo
  for select to authenticated using (public.soy_admin());

-- Rutinas (añadir y cambiar; leer ya puede todo el mundo)
drop policy if exists "admin anade rutinas" on rutinas;
create policy "admin anade rutinas" on rutinas
  for insert to authenticated with check (public.soy_admin());

drop policy if exists "admin cambia rutinas" on rutinas;
create policy "admin cambia rutinas" on rutinas
  for update to authenticated using (public.soy_admin()) with check (public.soy_admin());

-- Técnica de los ejercicios (leer, añadir y cambiar)
drop policy if exists "admin lee la tecnica" on tecnica_ejercicios;
create policy "admin lee la tecnica" on tecnica_ejercicios
  for select to authenticated using (public.soy_admin());

drop policy if exists "admin anade tecnica" on tecnica_ejercicios;
create policy "admin anade tecnica" on tecnica_ejercicios
  for insert to authenticated with check (public.soy_admin());

drop policy if exists "admin cambia la tecnica" on tecnica_ejercicios;
create policy "admin cambia la tecnica" on tecnica_ejercicios
  for update to authenticated using (public.soy_admin()) with check (public.soy_admin());

-- Alimentación: banners, consejos y menús (leer y cambiar)
drop policy if exists "admin lee la alimentacion" on alimentacion;
create policy "admin lee la alimentacion" on alimentacion
  for select to authenticated using (public.soy_admin());

drop policy if exists "admin cambia la alimentacion" on alimentacion;
create policy "admin cambia la alimentacion" on alimentacion
  for update to authenticated using (public.soy_admin()) with check (public.soy_admin());

drop policy if exists "admin lee los menus" on menus_alimentacion;
create policy "admin lee los menus" on menus_alimentacion
  for select to authenticated using (public.soy_admin());

drop policy if exists "admin cambia los menus" on menus_alimentacion;
create policy "admin cambia los menus" on menus_alimentacion
  for update to authenticated using (public.soy_admin()) with check (public.soy_admin());


-- 4. AÑADIR A LOS 6 DEL EQUIPO (una sola vez) -------------------------------------------
-- Cada persona tiene que tener ya su cuenta en la web (registrada y con el correo confirmado).
-- Copiar estas líneas en una consulta NUEVA, cambiar el correo y el nombre, y pulsar Run.
-- (Así los correos no quedan guardados en este archivo, que se sube a GitHub.)
--
-- insert into administradores (auth_id, nombre)
-- select id, 'Marta' from auth.users where email = 'CORREO_DE_LA_CUENTA'
-- on conflict (auth_id) do nothing;
--
-- Para ver quién es administrador:
-- select a.nombre, u.email, a.desde from administradores a join auth.users u on u.id = a.auth_id;
--
-- Para quitar a alguien:
-- delete from administradores where nombre = 'NOMBRE';
