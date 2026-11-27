-- Pesas que apetece enseñar · Aceptar términos y condiciones (PVBPQAE-94, Mauro)
-- Pegar en Supabase: SQL Editor > New query > Run   (se puede ejecutar más de una vez)
-- Ejecutar DESPUÉS de 4_conectar_usuarios_con_cuentas.sql y 8_suscripcion_premium.sql.
--
-- Qué hace:
--   1. Añade la columna «fecha_terminos» a «Registro de usuarios»: el día y la hora en que la
--      persona aceptó los términos y condiciones y la política de privacidad al registrarse.
--      La web NO puede cambiarla (no está entre las columnas que se pueden editar).
--   2. Cambia la función que crea el perfil al registrarse (la del script 4) para que guarde esa
--      fecha cuando la persona ha marcado la casilla. El resto lo hace exactamente igual.
-- Las cuentas creadas antes de este script se quedan con la fecha vacía.


-- 1. Columna nueva -----------------------------------------------------------------
alter table "Registro de usuarios" add column if not exists fecha_terminos timestamptz;


-- 2. Crear el perfil al registrarse (igual que antes + fecha de aceptación) -------------
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
     primera_rutina_en_7_dias, activa_ultimos_30_dias, fecha_terminos)
  values
    (new.id,
     new.raw_user_meta_data ->> 'nombre',
     new.raw_user_meta_data ->> 'apellidos',
     new.email,
     (new.raw_user_meta_data ->> 'edad')::bigint,
     new.raw_user_meta_data ->> 'genero',
     (new.raw_user_meta_data ->> 'peso_pesa_kg')::bigint,
     current_date, 'Gratuito', false, 0, 0, false, false,
     case when (new.raw_user_meta_data ->> 'acepta_terminos') = 'true' then now() end);
  return new;
end;
$$;

-- El trigger «al_crear_cuenta» (script 4) ya llama a esta función: no hay que tocarlo.
