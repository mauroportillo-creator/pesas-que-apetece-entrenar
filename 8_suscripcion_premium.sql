-- Pesas que apetece enseñar · Suscripción Premium y tarjeta regalo (PVBPQAE-93, Marta)
-- Pegar en Supabase: SQL Editor > New query > Run   (se puede ejecutar más de una vez)
-- Ejecutar DESPUÉS de 4_conectar_usuarios_con_cuentas.sql.
--
-- Qué hace:
--   1. Crea la tabla «tarjetas_regalo» (una tarjeta por persona, se regala al hacerse Premium).
--   2. Protege las columnas del plan: la web solo puede cambiar nombre, apellidos, nivel y objetivo.
--      Así nadie puede ponerse Premium «a mano» desde fuera.
--   3. Crea la función hacerme_premium(), que es lo que llama el botón «Aceptar».
--
-- Las columnas «plan» (Gratuito / Premium) y «fecha_suscripcion» ya existen en «Registro de usuarios».
-- No hay pago real: la suscripción es simulada.


-- 1. Tarjetas regalo -------------------------------------------------------------
create table if not exists tarjetas_regalo (
  id         bigint generated always as identity primary key,
  auth_id    uuid not null unique default auth.uid() references auth.users(id) on delete cascade,
  codigo     text not null unique,
  importe    numeric(6, 2) not null default 10,
  creada     timestamptz not null default now(),
  usada      boolean not null default false,
  fecha_uso  timestamptz
);

-- Seguridad: cada persona solo ve SU tarjeta (RLS).
-- No hay permiso para crearlas ni cambiarlas desde la web: las crea la función de abajo.
-- (El descuento en el carrito, PVBPQAE-8, añadirá su propia función para marcarla como usada.)
alter table tarjetas_regalo enable row level security;

drop policy if exists "ver mi tarjeta" on tarjetas_regalo;
create policy "ver mi tarjeta" on tarjetas_regalo
  for select to authenticated using (auth_id = auth.uid());


-- 2. Proteger el plan --------------------------------------------------------------
-- Hasta ahora, la regla «editar mi perfil» dejaba cambiar cualquier columna del propio perfil,
-- también «plan». Ahora la web solo puede cambiar estas cuatro (las de «Mis datos» y el cuestionario).
-- Si otra historia necesita guardar una columna nueva desde la web, hay que añadirla aquí.
revoke update on "Registro de usuarios" from anon, authenticated;
grant update ("Nombre", apellidos, nivel, objetivo) on "Registro de usuarios" to authenticated;


-- 3. Hacerse Premium ---------------------------------------------------------------
-- Cambia el plan de la persona que ha iniciado sesión (nunca el de otra) y le regala su tarjeta.
-- Si ya tenía tarjeta (por ejemplo, se dio de baja y vuelve), no se crea otra.
create or replace function public.hacerme_premium()
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
  yo uuid := auth.uid();
begin
  if yo is null then
    raise exception 'Hay que iniciar sesión para suscribirse';
  end if;

  update "Registro de usuarios"
     set plan = 'Premium', fecha_suscripcion = current_date
   where auth_id = yo;

  if not exists (select 1 from tarjetas_regalo where auth_id = yo) then
    insert into tarjetas_regalo (auth_id, codigo, importe)
    values (yo,
            'PREMIUM-' || upper(substr(md5(random()::text || clock_timestamp()::text), 1, 6)),
            10);
  end if;
end;
$$;

-- Solo la pueden usar las personas con sesión iniciada
revoke all on function public.hacerme_premium() from public, anon;
grant execute on function public.hacerme_premium() to authenticated;

-- Si se elimina la cuenta, su tarjeta se borra sola (on delete cascade).
