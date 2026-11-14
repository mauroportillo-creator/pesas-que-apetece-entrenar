-- Pesas que apetece enseñar · Eliminar mi cuenta (RGPD, PVBPQAE-56)
-- Pegar en Supabase: SQL Editor > New query > Run   (se puede ejecutar más de una vez)
-- Ejecutar DESPUÉS de 4_conectar_usuarios_con_cuentas.sql y 5_crear_tabla_rutinas_guardadas.sql.
--
-- La web llama a esta función cuando alguien pulsa «Eliminar mi cuenta» en «Mis datos».
-- Borra SOLO la cuenta de la persona que ha iniciado sesión (auth.uid()), nunca la de otra.
-- Hace falta una función porque la clave pública de la web no puede borrar cuentas por sí sola.

create or replace function public.eliminar_mi_cuenta()
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
  yo uuid := auth.uid();
begin
  if yo is null then
    raise exception 'Hay que iniciar sesión para eliminar la cuenta';
  end if;

  -- 1. Sus rutinas guardadas (la estrella)
  delete from rutinas_guardadas where auth_id = yo;
  -- 2. Su perfil
  delete from "Registro de usuarios" where auth_id = yo;
  -- 3. Su cuenta: correo y contraseña de Supabase Authentication
  delete from auth.users where id = yo;
end;
$$;

-- Solo la pueden usar las personas con sesión iniciada
revoke all on function public.eliminar_mi_cuenta() from public, anon;
grant execute on function public.eliminar_mi_cuenta() to authenticated;
