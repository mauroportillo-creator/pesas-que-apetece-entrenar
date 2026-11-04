-- Pesas que apetece enseñar · Tabla de usuarios sintéticos
-- Pegar en Supabase: SQL Editor > New query > Run

create table if not exists usuarios_sinteticos (
  id_usuario                text primary key,
  fecha_registro            date,
  edad                      int,
  genero                    text,
  peso_pesa_kg              int,
  nivel                     text,
  objetivo                  text,
  fecha_primera_rutina      date,
  primera_rutina_en_7_dias  boolean,
  rutinas_completadas       int,
  fecha_ultima_actividad    date,
  activa_ultimos_30_dias    boolean,
  racha_semanas             int,
  plan                      text,
  fecha_suscripcion         date,
  unido_a_reto              boolean
);

-- Seguridad: tabla privada (nadie la lee desde la web, solo desde el panel de Supabase)
alter table usuarios_sinteticos enable row level security;
