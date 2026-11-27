-- Pesas que apetece enseñar · Cancelar la suscripción Premium (PVBPQAE-20, Mauro)
-- Pegar en Supabase: SQL Editor > New query > Run   (se puede ejecutar más de una vez)
-- Ejecutar DESPUÉS de 8_suscripcion_premium.sql.
--
-- Qué hace:
--   1. Añade la columna «fecha_fin_premium» a «Registro de usuarios»: vacía si la suscripción se
--      renueva; con una fecha si la persona ha cancelado (hasta ese día sigue siendo Premium).
--      La web NO puede cambiarla directamente (no está entre las columnas que se pueden editar).
--   2. cancelar_premium(): lo que llama el botón «Sí, cancelar». Desactiva la renovación y
--      devuelve el último día de Premium (el día antes de la siguiente renovación mensual).
--   3. quitar_premium_terminado(): cuando ya ha pasado esa fecha, el plan vuelve a «Gratuito».
--   4. hacerme_premium() (la de la PVBPQAE-93) ahora también borra la fecha de fin,
--      por si alguien que había cancelado se vuelve a suscribir.
-- Cada función solo cambia el perfil de la persona que ha iniciado sesión, nunca el de otra.
-- No hay pago real: la suscripción es simulada.


-- 1. Columna nueva -----------------------------------------------------------------
alter table "Registro de usuarios" add column if not exists fecha_fin_premium date;


-- 2. Cancelar la suscripción ---------------------------------------------------------
create or replace function public.cancelar_premium()
returns date
language plpgsql
security definer
set search_path = public
as $$
declare
  yo     uuid := auth.uid();
  mi_plan text;
  desde  date;
  ya_fin date;
  meses  int := 1;
begin
  if yo is null then
    raise exception 'Hay que iniciar sesión para cancelar la suscripción';
  end if;

  select plan, fecha_suscripcion, fecha_fin_premium into mi_plan, desde, ya_fin
    from "Registro de usuarios" where auth_id = yo;

  if mi_plan is distinct from 'Premium' then
    raise exception 'No tienes una suscripción Premium activa';
  end if;
  if ya_fin is not null then
    return ya_fin;  -- ya estaba cancelada: no cambia nada
  end if;

  -- Siguiente renovación mensual a partir de hoy (si se suscribió el 15, se renueva cada día 15)
  desde := coalesce(desde, current_date);
  while (desde + make_interval(months => meses))::date <= current_date loop
    meses := meses + 1;
  end loop;

  update "Registro de usuarios"
     set fecha_fin_premium = (desde + make_interval(months => meses))::date - 1
   where auth_id = yo
  returning fecha_fin_premium into ya_fin;

  return ya_fin;
end;
$$;


-- 3. Pasar a gratuito cuando termina -------------------------------------------------
create or replace function public.quitar_premium_terminado()
returns void
language sql
security definer
set search_path = public
as $$
  update "Registro de usuarios"
     set plan = 'Gratuito', fecha_fin_premium = null
   where auth_id = auth.uid()
     and plan = 'Premium'
     and fecha_fin_premium < current_date;
$$;


-- 4. Volver a suscribirse (misma función de la PVBPQAE-93 + borrar la fecha de fin) ------
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
     set plan = 'Premium', fecha_suscripcion = current_date, fecha_fin_premium = null
   where auth_id = yo;

  if not exists (select 1 from tarjetas_regalo where auth_id = yo) then
    insert into tarjetas_regalo (auth_id, codigo, importe)
    values (yo,
            'PREMIUM-' || upper(substr(md5(random()::text || clock_timestamp()::text), 1, 6)),
            10);
  end if;
end;
$$;


-- Solo las pueden usar las personas con sesión iniciada
revoke all on function public.cancelar_premium() from public, anon;
grant execute on function public.cancelar_premium() to authenticated;
revoke all on function public.quitar_premium_terminado() from public, anon;
grant execute on function public.quitar_premium_terminado() to authenticated;
revoke all on function public.hacerme_premium() from public, anon;
grant execute on function public.hacerme_premium() to authenticated;
