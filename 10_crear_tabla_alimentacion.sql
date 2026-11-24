-- Pesas que apetece enseñar · Consejos de alimentación según el objetivo (PVBPQAE-98)
-- Pegar en Supabase: SQL Editor > New query > Run   (se puede ejecutar más de una vez)
-- Ejecutar DESPUÉS de 8_suscripcion_premium.sql.
--
-- Qué hace:
--   1. Crea dos tablas:
--      · «alimentacion»: una fila por objetivo con su banner (titular, subtítulo y color)
--        y sus 5 consejos.
--      · «menus_alimentacion»: el menú semanal de cada objetivo, una fila por comida
--        (5 objetivos × 7 días × 5 tomas = 175 filas) con cantidades, kcal y macros.
--   2. Carga todo el contenido del documento «Pesas_Alimentacion_Sprint2» (María).
--   3. Seguridad: solo las personas Premium pueden leerlas (la alimentación es contenido Premium).
--
-- OJO: si se vuelve a ejecutar, el contenido vuelve a ser el del documento (se pierden los
-- cambios hechos a mano en Supabase). Para cambiar un texto, mejor hacerlo en Table Editor.


-- 1. Tablas -----------------------------------------------------------------------
create table if not exists alimentacion (
  objetivo     text primary key            -- igual que en el cuestionario: Tonificar, Ganar fuerza…
);
alter table alimentacion add column if not exists titular     text;   -- titular del banner
alter table alimentacion add column if not exists subtitulo   text;   -- subtítulo del banner
alter table alimentacion add column if not exists color       text;   -- color del banner (#2E7D6B)
alter table alimentacion add column if not exists consejos    text;   -- un consejo por línea: «Título | texto»
alter table alimentacion add column if not exists actualizado timestamptz not null default now();

create table if not exists menus_alimentacion (
  id           bigint generated always as identity primary key,
  objetivo     text not null references alimentacion(objetivo) on delete cascade,
  dia          smallint not null check (dia between 1 and 7),     -- 1 = lunes … 7 = domingo
  orden        smallint not null check (orden between 1 and 5),   -- 1 = desayuno … 5 = cena
  toma         text not null,                                      -- Desayuno, Media mañana…
  plato        text not null,
  ingredientes text,                                               -- cantidades, separadas por «;»
  kcal         integer,
  proteinas    integer,                                            -- gramos
  hidratos     integer,                                            -- gramos
  grasas       integer,                                            -- gramos
  unique (objetivo, dia, orden)
);


-- 2. Contenido: banners y consejos ------------------------------------------------
insert into alimentacion (objetivo, titular, subtitulo, color, consejos) values
  ('Tonificar', 'Proteína en cada comida, energía para entrenar', 'Tonificar es ganar músculo y perder algo de grasa a la vez: come lo justo y reparte bien la proteína.', '#2E7D6B',
   'Proteína en todas las comidas | Incluye una fuente de proteína (huevo, pescado, carne magra, legumbres, lácteos) en cada comida principal para mantener y construir músculo.
Calorías cerca de tu mantenimiento | Ni dieta estricta ni comer de más: sin grandes déficits ni excesos, tu cuerpo recompone mejor (menos grasa, más músculo).
Hidratos a tu favor | Arroz, pasta, patata, avena o fruta en la comida previa y posterior al entreno te ayudan a rendir y a recuperarte.
Verduras y fibra a diario | Que la verdura ocupe aproximadamente la mitad del plato en comidas y cenas: sacia y aporta vitaminas y minerales.
Hidratación y descanso | Bebe agua a lo largo del día y procura dormir entre 7 y 9 horas: sin descanso, la recuperación se resiente.'),
  ('Perder peso', 'Un déficit pequeño, constante y sostenible', 'Perder peso sin pasar hambre: prioriza lo que sacia y huye de las dietas extremas.', '#1F6FB2',
   'Déficit moderado | Reduce entre un 10 y un 20 % tu ingesta de mantenimiento (unas 300–500 kcal): suele traducirse en unos 0,3–0,5 kg por semana, un ritmo sostenible.
Proteína alta para conservar músculo | Una buena ración de proteína en cada comida sacia más y ayuda a proteger tu masa muscular mientras pierdes grasa.
Llena el plato de verdura y fruta | Aportan mucho volumen y pocas calorías. Empieza comidas y cenas por una ensalada o una verdura.
Cuida las calorías líquidas y los ultraprocesados | Refrescos, zumos, bollería y snacks suman muchas kcal sin saciar. Deja el agua como bebida base.
Ni saltarte comidas ni dietas milagro | Comer con regularidad evita los atracones; si un plan es demasiado restrictivo, no se puede mantener.'),
  ('Ganar fuerza', 'Combustible para levantar más', 'Para progresar en fuerza necesitas energía suficiente: come lo bastante, sobre todo hidratos y proteína.', '#9C2F2F',
   'Un pequeño superávit | Unas 200–300 kcal por encima de tu mantenimiento (un 10–15 %) permiten progresar sin acumular grasa de más.
Proteína bien repartida | Apunta a 1,6–2,2 g de proteína por kg de peso y día, repartidos en 3–5 tomas.
Hidratos antes y después de entrenar | Son el combustible principal del entrenamiento intenso: arroz, pasta, pan integral, patata o fruta.
No entrenes sin energía | Una comida o un snack entre 1 y 3 horas antes mejora el rendimiento en las series pesadas.
Grasas saludables y buena hidratación | Aceite de oliva virgen extra, frutos secos y pescado azul, y agua durante todo el día.'),
  ('Salud general', 'Comer bien, cada día', 'Un patrón variado y de estilo mediterráneo es la mejor base para sentirte bien y entrenar mejor.', '#3C7D3F',
   'Verdura y fruta a diario | Procura al menos 5 raciones al día, de varios colores y de temporada.
Legumbres y pescado cada semana | Legumbres 3–4 veces por semana y pescado 2–3 veces, incluyendo pescado azul alguna vez.
Cereales integrales y grasas de calidad | Pan, pasta y arroz integrales; aceite de oliva virgen extra y un puñado de frutos secos al día.
Menos ultraprocesados, sal y azúcar añadido | Deja los dulces, la bollería, los embutidos y los fritos para ocasiones puntuales.
Agua y comidas sin prisa | El agua como bebida habitual y comer despacio, con horarios regulares, ayudan a notar mejor el hambre y la saciedad.'),
  ('Constancia', 'La mejor dieta es la que puedes mantener', 'La regularidad gana a la perfección: hazlo fácil, planifica y no te castigues si un día fallas.', '#6A4C93',
   'Planifica la semana | Dedica 30 minutos a decidir los menús y la lista de la compra, y cocina en tanda uno o dos días.
Rutinas simples | Repite desayunos y cenas sencillos y rota solo la comida principal: menos decisiones, más constancia.
La regla del 80/20 | Come bien la mayor parte del tiempo y deja margen para caprichos sin culpa.
Un fallo no arruina la semana | Retoma en la siguiente comida, sin compensar con ayunos ni castigos.
Ten siempre un plan B | Atún en lata, huevos, fruta, yogur y frutos secos a mano para los días con poco tiempo.')
on conflict (objetivo) do update set
  titular = excluded.titular, subtitulo = excluded.subtitulo, color = excluded.color,
  consejos = excluded.consejos, actualizado = now();


-- 3. Contenido: menús semanales -------------------------------------------------------
insert into menus_alimentacion (objetivo, dia, orden, toma, plato, ingredientes, kcal, proteinas, hidratos, grasas) values
  ('Tonificar', 1, 1, 'Desayuno', 'Bol de yogur griego con avena, plátano y nueces', 'Yogur griego natural 150 g; Copos de avena 45 g; 1 plátano (100 g); Nueces 10 g', 462, 22, 54, 17),
  ('Tonificar', 1, 2, 'Media mañana', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 125 g; Fresas 150 g; Almendras 10 g', 186, 8, 18, 9),
  ('Tonificar', 1, 3, 'Comida', 'Pollo a la plancha con arroz integral y verduras salteadas', 'Pechuga de pollo (peso en crudo) 150 g; Arroz integral (peso en crudo) 70 g; Verdura variada (cocinada o salteada) 250 g; Aceite de oliva virgen extra (1 cda., 10 g); 1 pieza de fruta (150 g)', 637, 46, 80, 15),
  ('Tonificar', 1, 4, 'Merienda', 'Mini bocadillo de pavo y tomate', 'Pan integral (2 rebanadas, 60 g); Pechuga de pavo en lonchas 40 g; Tomate 60 g', 194, 13, 29, 3),
  ('Tonificar', 1, 5, 'Cena', 'Tortilla francesa de 3 huevos con ensalada y pan integral', '3 huevos (150 g); Ensalada (lechuga, tomate, zanahoria…) 200 g; Pan integral (2 rebanadas, 60 g); Aceite de oliva virgen extra (0,5 cda., 5 g)', 441, 27, 34, 22),
  ('Tonificar', 2, 1, 'Desayuno', 'Tostadas integrales con huevo, aguacate y naranja', 'Pan integral (2 rebanadas, 60 g); 2 huevos (100 g); Aguacate 40 g; Tomate 80 g; 1 naranja (150 g)', 435, 21, 47, 18),
  ('Tonificar', 2, 2, 'Media mañana', 'Fruta y puñado de almendras', '1 manzana (150 g); Almendras 20 g', 197, 5, 21, 10),
  ('Tonificar', 2, 3, 'Comida', 'Salmón al horno con patata y ensalada', 'Salmón (peso en crudo) 150 g; Patata (peso en crudo) 250 g; Ensalada (lechuga, tomate, zanahoria…) 200 g; Aceite de oliva virgen extra (0,5 cda., 5 g); 1 pieza de fruta (150 g)', 652, 38, 68, 25),
  ('Tonificar', 2, 4, 'Merienda', 'Queso fresco batido con arándanos y nueces', 'Queso fresco batido 0 % 150 g; Arándanos 75 g; Nueces 10 g', 181, 14, 15, 7),
  ('Tonificar', 2, 5, 'Cena', 'Pechuga de pavo con boniato asado y verduras', 'Pechuga de pavo (peso en crudo) 150 g; Boniato (peso en crudo) 200 g; Verdura variada (cocinada o salteada) 250 g; Aceite de oliva virgen extra (1 cda., 10 g)', 486, 43, 50, 12),
  ('Tonificar', 3, 1, 'Desayuno', 'Porridge de avena con leche, manzana y crema de cacahuete', 'Copos de avena 50 g; Leche semidesnatada 250 ml; 1 manzana (150 g); Crema de cacahuete 100 % 10 g', 439, 18, 63, 13),
  ('Tonificar', 3, 2, 'Media mañana', 'Mini bocadillo de pavo y tomate', 'Pan integral (2 rebanadas, 60 g); Pechuga de pavo en lonchas 40 g; Tomate 60 g', 194, 13, 29, 3),
  ('Tonificar', 3, 3, 'Comida', 'Lentejas estofadas con verduras y huevo duro', 'Lentejas cocidas 300 g; 2 huevos (100 g); Verdura variada (cocinada o salteada) 150 g; Aceite de oliva virgen extra (1 cda., 10 g); 1 pieza de fruta (150 g)', 677, 43, 76, 22),
  ('Tonificar', 3, 4, 'Merienda', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 125 g; Fresas 150 g; Almendras 10 g', 186, 8, 18, 9),
  ('Tonificar', 3, 5, 'Cena', 'Merluza al horno con patata cocida y judías verdes', 'Merluza (peso en crudo) 200 g; Patata (peso en crudo) 200 g; Verdura variada (cocinada o salteada) 250 g; Aceite de oliva virgen extra (1 cda., 10 g)', 465, 43, 44, 13),
  ('Tonificar', 4, 1, 'Desayuno', 'Bol de yogur griego con avena, plátano y nueces', 'Yogur griego natural 150 g; Copos de avena 45 g; 1 plátano (100 g); Nueces 10 g', 462, 22, 54, 17),
  ('Tonificar', 4, 2, 'Media mañana', 'Queso fresco batido con arándanos y nueces', 'Queso fresco batido 0 % 150 g; Arándanos 75 g; Nueces 10 g', 181, 14, 15, 7),
  ('Tonificar', 4, 3, 'Comida', 'Pasta integral con ternera magra y tomate natural', 'Pasta integral (peso en crudo) 70 g; Ternera magra (peso en crudo) 130 g; Tomate 200 g; Aceite de oliva virgen extra (1 cda., 10 g); Verdura variada (cocinada o salteada) 150 g; 1 pieza de fruta (150 g)', 649, 41, 77, 19),
  ('Tonificar', 4, 4, 'Merienda', 'Fruta y puñado de almendras', '1 manzana (150 g); Almendras 20 g', 197, 5, 21, 10),
  ('Tonificar', 4, 5, 'Cena', 'Ensalada completa de atún, huevo y garbanzos', 'Atún al natural (escurrido) 100 g; 1 huevo (50 g); Garbanzos cocidos 120 g; Ensalada (lechuga, tomate, zanahoria…) 250 g; Aceite de oliva virgen extra (1 cda., 10 g)', 479, 44, 31, 20),
  ('Tonificar', 5, 1, 'Desayuno', 'Tostadas integrales con huevo, aguacate y naranja', 'Pan integral (2 rebanadas, 60 g); 2 huevos (100 g); Aguacate 40 g; Tomate 80 g; 1 naranja (150 g)', 435, 21, 47, 18),
  ('Tonificar', 5, 2, 'Media mañana', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 125 g; Fresas 150 g; Almendras 10 g', 186, 8, 18, 9),
  ('Tonificar', 5, 3, 'Comida', 'Merluza con quinoa y brócoli', 'Merluza (peso en crudo) 200 g; Quinoa (peso en crudo) 65 g; Verdura variada (cocinada o salteada) 250 g; Aceite de oliva virgen extra (1 cda., 10 g); 1 pieza de fruta (150 g)', 617, 49, 67, 17),
  ('Tonificar', 5, 4, 'Merienda', 'Mini bocadillo de pavo y tomate', 'Pan integral (2 rebanadas, 60 g); Pechuga de pavo en lonchas 40 g; Tomate 60 g', 194, 13, 29, 3),
  ('Tonificar', 5, 5, 'Cena', 'Pollo salteado con verduras y arroz integral', 'Pechuga de pollo (peso en crudo) 150 g; Arroz integral (peso en crudo) 45 g; Verdura variada (cocinada o salteada) 300 g; Aceite de oliva virgen extra (1 cda., 10 g)', 485, 44, 45, 14),
  ('Tonificar', 6, 1, 'Desayuno', 'Porridge de avena con leche, manzana y crema de cacahuete', 'Copos de avena 50 g; Leche semidesnatada 250 ml; 1 manzana (150 g); Crema de cacahuete 100 % 10 g', 439, 18, 63, 13),
  ('Tonificar', 6, 2, 'Media mañana', 'Fruta y puñado de almendras', '1 manzana (150 g); Almendras 20 g', 197, 5, 21, 10),
  ('Tonificar', 6, 3, 'Comida', 'Garbanzos con espinacas y pechuga de pavo', 'Garbanzos cocidos 280 g; Pechuga de pavo (peso en crudo) 100 g; Verdura variada (cocinada o salteada) 200 g; Aceite de oliva virgen extra (1 cda., 10 g)', 613, 50, 58, 20),
  ('Tonificar', 6, 4, 'Merienda', 'Queso fresco batido con arándanos y nueces', 'Queso fresco batido 0 % 150 g; Arándanos 75 g; Nueces 10 g', 181, 14, 15, 7),
  ('Tonificar', 6, 5, 'Cena', 'Salmón a la plancha con calabacín y quinoa', 'Salmón (peso en crudo) 120 g; Quinoa (peso en crudo) 45 g; Verdura variada (cocinada o salteada) 250 g; Aceite de oliva virgen extra (0,5 cda., 5 g)', 506, 35, 37, 24),
  ('Tonificar', 7, 1, 'Desayuno', 'Bol de yogur griego con avena, plátano y nueces', 'Yogur griego natural 150 g; Copos de avena 45 g; 1 plátano (100 g); Nueces 10 g', 462, 22, 54, 17),
  ('Tonificar', 7, 2, 'Media mañana', 'Mini bocadillo de pavo y tomate', 'Pan integral (2 rebanadas, 60 g); Pechuga de pavo en lonchas 40 g; Tomate 60 g', 194, 13, 29, 3),
  ('Tonificar', 7, 3, 'Comida', 'Arroz con atún, huevo y ensalada', 'Arroz integral (peso en crudo) 70 g; Atún al natural (escurrido) 120 g; 1 huevo (50 g); Ensalada (lechuga, tomate, zanahoria…) 200 g; Aceite de oliva virgen extra (1 cda., 10 g); 1 pieza de fruta (150 g)', 656, 45, 77, 19),
  ('Tonificar', 7, 4, 'Merienda', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 125 g; Fresas 150 g; Almendras 10 g', 186, 8, 18, 9),
  ('Tonificar', 7, 5, 'Cena', 'Crema de verduras con tostadas de pavo y queso fresco', 'Verdura variada (cocinada o salteada) 350 g; Pan integral (2 rebanadas, 60 g); Pechuga de pavo en lonchas 80 g; Queso fresco batido 0 % 125 g; Aceite de oliva virgen extra (0,5 cda., 5 g)', 424, 37, 46, 10),
  ('Perder peso', 1, 1, 'Desayuno', 'Tostadas integrales con huevo, aguacate y naranja', 'Pan integral (2 rebanadas, 60 g); 2 huevos (100 g); Aguacate 30 g; Tomate 60 g; Naranja 100 g', 391, 20, 41, 17),
  ('Perder peso', 1, 2, 'Media mañana', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 100 g; Fresas 125 g; Almendras 10 g', 162, 7, 15, 8),
  ('Perder peso', 1, 3, 'Comida', 'Merluza con quinoa y brócoli', 'Merluza (peso en crudo) 200 g; Quinoa (peso en crudo) 45 g; Verdura variada (cocinada o salteada) 300 g; Aceite de oliva virgen extra (0,5 cda., 5 g); 1 pieza de fruta (150 g)', 515, 47, 57, 11),
  ('Perder peso', 1, 4, 'Merienda', 'Queso fresco batido con arándanos y nueces', 'Queso fresco batido 0 % 125 g; Arándanos 75 g; Nueces 10 g', 168, 12, 14, 7),
  ('Perder peso', 1, 5, 'Cena', 'Pechuga de pavo con boniato asado y verduras', 'Pechuga de pavo (peso en crudo) 150 g; Boniato (peso en crudo) 140 g; Verdura variada (cocinada o salteada) 300 g; Aceite de oliva virgen extra (0,5 cda., 5 g)', 402, 43, 40, 8),
  ('Perder peso', 2, 1, 'Desayuno', 'Bol de yogur griego con avena, plátano y nueces', 'Yogur griego natural 125 g; Copos de avena 35 g; 1 plátano (100 g); Nueces 10 g', 403, 18, 47, 16),
  ('Perder peso', 2, 2, 'Media mañana', 'Fruta y puñado de almendras', 'Manzana 100 g; Almendras 15 g', 141, 3, 14, 8),
  ('Perder peso', 2, 3, 'Comida', 'Pollo a la plancha con arroz integral y verduras salteadas', 'Pechuga de pollo (peso en crudo) 150 g; Arroz integral (peso en crudo) 50 g; Verdura variada (cocinada o salteada) 300 g; Aceite de oliva virgen extra (0,5 cda., 5 g); 1 pieza de fruta (150 g)', 536, 45, 67, 10),
  ('Perder peso', 2, 4, 'Merienda', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 100 g; Fresas 125 g; Almendras 10 g', 162, 7, 15, 8),
  ('Perder peso', 2, 5, 'Cena', 'Crema de verduras con tostadas de pavo y queso fresco', 'Verdura variada (cocinada o salteada) 425 g; Pan integral (1 rebanada, 30 g); Pechuga de pavo en lonchas 80 g; Queso fresco batido 0 % 125 g; Aceite de oliva virgen extra (0,5 cda., 5 g)', 373, 36, 37, 9),
  ('Perder peso', 3, 1, 'Desayuno', 'Porridge de avena con leche, manzana y crema de cacahuete', 'Copos de avena 40 g; Leche semidesnatada 200 ml; Manzana 100 g; Crema de cacahuete 100 % 10 g', 352, 15, 48, 11),
  ('Perder peso', 3, 2, 'Media mañana', 'Queso fresco batido con arándanos y nueces', 'Queso fresco batido 0 % 125 g; Arándanos 75 g; Nueces 10 g', 168, 12, 14, 7),
  ('Perder peso', 3, 3, 'Comida', 'Lentejas estofadas con verduras y huevo duro', 'Lentejas cocidas 210 g; 2 huevos (100 g); Verdura variada (cocinada o salteada) 175 g; Aceite de oliva virgen extra (0,5 cda., 5 g); 1 pieza de fruta (150 g)', 541, 36, 61, 17),
  ('Perder peso', 3, 4, 'Merienda', 'Fruta y puñado de almendras', 'Manzana 100 g; Almendras 15 g', 141, 3, 14, 8),
  ('Perder peso', 3, 5, 'Cena', 'Ensalada completa de atún, huevo y garbanzos', 'Atún al natural (escurrido) 100 g; 1 huevo (50 g); Garbanzos cocidos 80 g; Ensalada (lechuga, tomate, zanahoria…) 300 g; Aceite de oliva virgen extra (0,5 cda., 5 g)', 392, 41, 25, 14),
  ('Perder peso', 4, 1, 'Desayuno', 'Tostadas integrales con huevo, aguacate y naranja', 'Pan integral (2 rebanadas, 60 g); 2 huevos (100 g); Aguacate 30 g; Tomate 60 g; Naranja 100 g', 391, 20, 41, 17),
  ('Perder peso', 4, 2, 'Media mañana', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 100 g; Fresas 125 g; Almendras 10 g', 162, 7, 15, 8),
  ('Perder peso', 4, 3, 'Comida', 'Salmón al horno con patata y ensalada', 'Salmón (peso en crudo) 150 g; Patata (peso en crudo) 180 g; Ensalada (lechuga, tomate, zanahoria…) 250 g; Aceite de oliva virgen extra (0,5 cda., 5 g); 1 pieza de fruta (150 g)', 609, 38, 57, 25),
  ('Perder peso', 4, 4, 'Merienda', 'Queso fresco batido con arándanos y nueces', 'Queso fresco batido 0 % 125 g; Arándanos 75 g; Nueces 10 g', 168, 12, 14, 7),
  ('Perder peso', 4, 5, 'Cena', 'Tortilla francesa de 3 huevos con ensalada y pan integral', '3 huevos (150 g); Ensalada (lechuga, tomate, zanahoria…) 250 g; Pan integral (1 rebanada, 30 g); Aceite de oliva virgen extra (0,5 cda., 5 g)', 381, 24, 23, 21),
  ('Perder peso', 5, 1, 'Desayuno', 'Bol de yogur griego con avena, plátano y nueces', 'Yogur griego natural 125 g; Copos de avena 35 g; 1 plátano (100 g); Nueces 10 g', 403, 18, 47, 16),
  ('Perder peso', 5, 2, 'Media mañana', 'Fruta y puñado de almendras', 'Manzana 100 g; Almendras 15 g', 141, 3, 14, 8),
  ('Perder peso', 5, 3, 'Comida', 'Garbanzos con espinacas y pechuga de pavo', 'Garbanzos cocidos 200 g; Pechuga de pavo (peso en crudo) 100 g; Verdura variada (cocinada o salteada) 250 g; Aceite de oliva virgen extra (0,5 cda., 5 g)', 477, 45, 46, 13),
  ('Perder peso', 5, 4, 'Merienda', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 100 g; Fresas 125 g; Almendras 10 g', 162, 7, 15, 8),
  ('Perder peso', 5, 5, 'Cena', 'Merluza al horno con patata cocida y judías verdes', 'Merluza (peso en crudo) 200 g; Patata (peso en crudo) 140 g; Verdura variada (cocinada o salteada) 300 g; Aceite de oliva virgen extra (0,5 cda., 5 g)', 387, 43, 36, 8),
  ('Perder peso', 6, 1, 'Desayuno', 'Porridge de avena con leche, manzana y crema de cacahuete', 'Copos de avena 40 g; Leche semidesnatada 200 ml; Manzana 100 g; Crema de cacahuete 100 % 10 g', 352, 15, 48, 11),
  ('Perder peso', 6, 2, 'Media mañana', 'Queso fresco batido con arándanos y nueces', 'Queso fresco batido 0 % 125 g; Arándanos 75 g; Nueces 10 g', 168, 12, 14, 7),
  ('Perder peso', 6, 3, 'Comida', 'Pasta integral con ternera magra y tomate natural', 'Pasta integral (peso en crudo) 50 g; Ternera magra (peso en crudo) 130 g; Tomate 240 g; Aceite de oliva virgen extra (0,5 cda., 5 g); Verdura variada (cocinada o salteada) 175 g; 1 pieza de fruta (150 g)', 552, 40, 66, 14),
  ('Perder peso', 6, 4, 'Merienda', 'Fruta y puñado de almendras', 'Manzana 100 g; Almendras 15 g', 141, 3, 14, 8),
  ('Perder peso', 6, 5, 'Cena', 'Pollo salteado con verduras y arroz integral', 'Pechuga de pollo (peso en crudo) 150 g; Arroz integral (peso en crudo) 30 g; Verdura variada (cocinada o salteada) 350 g; Aceite de oliva virgen extra (0,5 cda., 5 g)', 401, 44, 36, 9),
  ('Perder peso', 7, 1, 'Desayuno', 'Tostadas integrales con huevo, aguacate y naranja', 'Pan integral (2 rebanadas, 60 g); 2 huevos (100 g); Aguacate 30 g; Tomate 60 g; Naranja 100 g', 391, 20, 41, 17),
  ('Perder peso', 7, 2, 'Media mañana', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 100 g; Fresas 125 g; Almendras 10 g', 162, 7, 15, 8),
  ('Perder peso', 7, 3, 'Comida', 'Arroz con atún, huevo y ensalada', 'Arroz integral (peso en crudo) 50 g; Atún al natural (escurrido) 120 g; 1 huevo (50 g); Ensalada (lechuga, tomate, zanahoria…) 250 g; Aceite de oliva virgen extra (0,5 cda., 5 g); 1 pieza de fruta (150 g)', 551, 44, 64, 13),
  ('Perder peso', 7, 4, 'Merienda', 'Queso fresco batido con arándanos y nueces', 'Queso fresco batido 0 % 125 g; Arándanos 75 g; Nueces 10 g', 168, 12, 14, 7),
  ('Perder peso', 7, 5, 'Cena', 'Salmón a la plancha con calabacín y quinoa', 'Salmón (peso en crudo) 120 g; Quinoa (peso en crudo) 30 g; Verdura variada (cocinada o salteada) 300 g; Aceite de oliva virgen extra (0,5 cda., 5 g)', 467, 34, 30, 23),
  ('Ganar fuerza', 1, 1, 'Desayuno', 'Bol de yogur griego con avena, plátano y nueces', 'Yogur griego natural 175 g; Copos de avena 55 g; 1 plátano (100 g); Nueces 10 g', 522, 26, 61, 19),
  ('Ganar fuerza', 1, 2, 'Media mañana', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 150 g; Fresas 175 g; Almendras 10 g', 210, 9, 21, 10),
  ('Ganar fuerza', 1, 3, 'Comida', 'Pollo a la plancha con arroz integral y verduras salteadas', 'Pechuga de pollo (peso en crudo) 170 g; Arroz integral (peso en crudo) 90 g; Verdura variada (cocinada o salteada) 250 g; Aceite de oliva virgen extra (1 cda., 10 g); Fruta de temporada 200 g', 754, 52, 101, 16),
  ('Ganar fuerza', 1, 4, 'Merienda', 'Mini bocadillo de pavo y tomate', 'Pan integral (2 rebanadas, 60 g); Pechuga de pavo en lonchas 50 g; Tomate 70 g', 206, 15, 29, 3),
  ('Ganar fuerza', 1, 5, 'Cena', 'Pechuga de pavo con boniato asado y verduras', 'Pechuga de pavo (peso en crudo) 170 g; Boniato (peso en crudo) 250 g; Verdura variada (cocinada o salteada) 250 g; Aceite de oliva virgen extra (1 cda., 10 g)', 550, 49, 60, 13),
  ('Ganar fuerza', 2, 1, 'Desayuno', 'Porridge de avena con leche, manzana y crema de cacahuete', 'Copos de avena 60 g; Leche semidesnatada 300 ml; Manzana 200 g; Crema de cacahuete 100 % 10 g', 526, 21, 78, 14),
  ('Ganar fuerza', 2, 2, 'Media mañana', 'Fruta y puñado de almendras', 'Manzana 200 g; Almendras 25 g', 253, 6, 28, 13),
  ('Ganar fuerza', 2, 3, 'Comida', 'Pasta integral con ternera magra y tomate natural', 'Pasta integral (peso en crudo) 90 g; Ternera magra (peso en crudo) 140 g; Tomate 200 g; Aceite de oliva virgen extra (1 cda., 10 g); Verdura variada (cocinada o salteada) 150 g; Fruta de temporada 200 g', 755, 46, 96, 20),
  ('Ganar fuerza', 2, 4, 'Merienda', 'Queso fresco batido con arándanos y nueces', 'Queso fresco batido 0 % 175 g; Arándanos 100 g; Nueces 10 g', 207, 16, 19, 7),
  ('Ganar fuerza', 2, 5, 'Cena', 'Tortilla francesa de 3 huevos con ensalada y pan integral', '3 huevos (150 g); Ensalada (lechuga, tomate, zanahoria…) 200 g; Pan integral (3 rebanadas, 90 g); Aceite de oliva virgen extra (0,5 cda., 5 g)', 512, 29, 47, 23),
  ('Ganar fuerza', 3, 1, 'Desayuno', 'Tostadas integrales con huevo, aguacate y naranja', 'Pan integral (2 rebanadas, 60 g); 2 huevos (100 g); Aguacate 50 g; Tomate 100 g; Naranja 200 g', 480, 22, 54, 20),
  ('Ganar fuerza', 3, 2, 'Media mañana', 'Mini bocadillo de pavo y tomate', 'Pan integral (2 rebanadas, 60 g); Pechuga de pavo en lonchas 50 g; Tomate 70 g', 206, 15, 29, 3),
  ('Ganar fuerza', 3, 3, 'Comida', 'Lentejas estofadas con verduras y huevo duro', 'Lentejas cocidas 380 g; 2 huevos (100 g); Verdura variada (cocinada o salteada) 150 g; Aceite de oliva virgen extra (1 cda., 10 g); Fruta de temporada 200 g', 790, 51, 95, 23),
  ('Ganar fuerza', 3, 4, 'Merienda', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 150 g; Fresas 175 g; Almendras 10 g', 210, 9, 21, 10),
  ('Ganar fuerza', 3, 5, 'Cena', 'Ensalada completa de atún, huevo y garbanzos', 'Atún al natural (escurrido) 110 g; 1 huevo (50 g); Garbanzos cocidos 150 g; Ensalada (lechuga, tomate, zanahoria…) 250 g; Aceite de oliva virgen extra (1 cda., 10 g)', 529, 49, 36, 21),
  ('Ganar fuerza', 4, 1, 'Desayuno', 'Bol de yogur griego con avena, plátano y nueces', 'Yogur griego natural 175 g; Copos de avena 55 g; 1 plátano (100 g); Nueces 10 g', 522, 26, 61, 19),
  ('Ganar fuerza', 4, 2, 'Media mañana', 'Queso fresco batido con arándanos y nueces', 'Queso fresco batido 0 % 175 g; Arándanos 100 g; Nueces 10 g', 207, 16, 19, 7),
  ('Ganar fuerza', 4, 3, 'Comida', 'Garbanzos con espinacas y pechuga de pavo', 'Garbanzos cocidos 350 g; Pechuga de pavo (peso en crudo) 110 g; Verdura variada (cocinada o salteada) 200 g; Aceite de oliva virgen extra (1 cda., 10 g)', 715, 58, 71, 22),
  ('Ganar fuerza', 4, 4, 'Merienda', 'Fruta y puñado de almendras', 'Manzana 200 g; Almendras 25 g', 253, 6, 28, 13),
  ('Ganar fuerza', 4, 5, 'Cena', 'Merluza al horno con patata cocida y judías verdes', 'Merluza (peso en crudo) 220 g; Patata (peso en crudo) 250 g; Verdura variada (cocinada o salteada) 250 g; Aceite de oliva virgen extra (1 cda., 10 g)', 518, 47, 53, 13),
  ('Ganar fuerza', 5, 1, 'Desayuno', 'Porridge de avena con leche, manzana y crema de cacahuete', 'Copos de avena 60 g; Leche semidesnatada 300 ml; Manzana 200 g; Crema de cacahuete 100 % 10 g', 526, 21, 78, 14),
  ('Ganar fuerza', 5, 2, 'Media mañana', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 150 g; Fresas 175 g; Almendras 10 g', 210, 9, 21, 10),
  ('Ganar fuerza', 5, 3, 'Comida', 'Salmón al horno con patata y ensalada', 'Salmón (peso en crudo) 170 g; Patata (peso en crudo) 310 g; Ensalada (lechuga, tomate, zanahoria…) 200 g; Aceite de oliva virgen extra (0,5 cda., 5 g); Fruta de temporada 200 g', 764, 44, 84, 28),
  ('Ganar fuerza', 5, 4, 'Merienda', 'Mini bocadillo de pavo y tomate', 'Pan integral (2 rebanadas, 60 g); Pechuga de pavo en lonchas 50 g; Tomate 70 g', 206, 15, 29, 3),
  ('Ganar fuerza', 5, 5, 'Cena', 'Crema de verduras con tostadas de pavo y queso fresco', 'Verdura variada (cocinada o salteada) 350 g; Pan integral (3 rebanadas, 90 g); Pechuga de pavo en lonchas 90 g; Queso fresco batido 0 % 150 g; Aceite de oliva virgen extra (0,5 cda., 5 g)', 517, 43, 61, 11),
  ('Ganar fuerza', 6, 1, 'Desayuno', 'Tostadas integrales con huevo, aguacate y naranja', 'Pan integral (2 rebanadas, 60 g); 2 huevos (100 g); Aguacate 50 g; Tomate 100 g; Naranja 200 g', 480, 22, 54, 20),
  ('Ganar fuerza', 6, 2, 'Media mañana', 'Fruta y puñado de almendras', 'Manzana 200 g; Almendras 25 g', 253, 6, 28, 13),
  ('Ganar fuerza', 6, 3, 'Comida', 'Arroz con atún, huevo y ensalada', 'Arroz integral (peso en crudo) 90 g; Atún al natural (escurrido) 130 g; 1 huevo (50 g); Ensalada (lechuga, tomate, zanahoria…) 200 g; Aceite de oliva virgen extra (1 cda., 10 g); Fruta de temporada 200 g', 762, 49, 98, 19),
  ('Ganar fuerza', 6, 4, 'Merienda', 'Queso fresco batido con arándanos y nueces', 'Queso fresco batido 0 % 175 g; Arándanos 100 g; Nueces 10 g', 207, 16, 19, 7),
  ('Ganar fuerza', 6, 5, 'Cena', 'Pollo salteado con verduras y arroz integral', 'Pechuga de pollo (peso en crudo) 170 g; Arroz integral (peso en crudo) 55 g; Verdura variada (cocinada o salteada) 300 g; Aceite de oliva virgen extra (1 cda., 10 g)', 541, 49, 53, 15),
  ('Ganar fuerza', 7, 1, 'Desayuno', 'Bol de yogur griego con avena, plátano y nueces', 'Yogur griego natural 175 g; Copos de avena 55 g; 1 plátano (100 g); Nueces 10 g', 522, 26, 61, 19),
  ('Ganar fuerza', 7, 2, 'Media mañana', 'Mini bocadillo de pavo y tomate', 'Pan integral (2 rebanadas, 60 g); Pechuga de pavo en lonchas 50 g; Tomate 70 g', 206, 15, 29, 3),
  ('Ganar fuerza', 7, 3, 'Comida', 'Pollo a la plancha con arroz integral y verduras salteadas', 'Pechuga de pollo (peso en crudo) 170 g; Arroz integral (peso en crudo) 90 g; Verdura variada (cocinada o salteada) 250 g; Aceite de oliva virgen extra (1 cda., 10 g); Fruta de temporada 200 g', 754, 52, 101, 16),
  ('Ganar fuerza', 7, 4, 'Merienda', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 150 g; Fresas 175 g; Almendras 10 g', 210, 9, 21, 10),
  ('Ganar fuerza', 7, 5, 'Cena', 'Salmón a la plancha con calabacín y quinoa', 'Salmón (peso en crudo) 130 g; Quinoa (peso en crudo) 55 g; Verdura variada (cocinada o salteada) 250 g; Aceite de oliva virgen extra (0,5 cda., 5 g)', 560, 39, 43, 26),
  ('Salud general', 1, 1, 'Desayuno', 'Porridge de avena con leche, manzana y crema de cacahuete', 'Copos de avena 50 g; Leche semidesnatada 250 ml; 1 manzana (150 g); Crema de cacahuete 100 % 10 g', 439, 18, 63, 13),
  ('Salud general', 1, 2, 'Media mañana', 'Fruta y puñado de almendras', '1 manzana (150 g); Almendras 20 g', 197, 5, 21, 10),
  ('Salud general', 1, 3, 'Comida', 'Lentejas estofadas con verduras y huevo duro', 'Lentejas cocidas 320 g; 2 huevos (100 g); Verdura variada (cocinada o salteada) 175 g; Aceite de oliva virgen extra (1 cda., 10 g); 1 pieza de fruta (150 g)', 705, 46, 80, 22),
  ('Salud general', 1, 4, 'Merienda', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 125 g; Fresas 150 g; Almendras 10 g', 186, 8, 18, 9),
  ('Salud general', 1, 5, 'Cena', 'Merluza al horno con patata cocida y judías verdes', 'Merluza (peso en crudo) 180 g; Patata (peso en crudo) 210 g; Verdura variada (cocinada o salteada) 275 g; Aceite de oliva virgen extra (1 cda., 10 g)', 464, 40, 47, 13),
  ('Salud general', 2, 1, 'Desayuno', 'Bol de yogur griego con avena, plátano y nueces', 'Yogur griego natural 150 g; Copos de avena 45 g; 1 plátano (100 g); Nueces 10 g', 462, 22, 54, 17),
  ('Salud general', 2, 2, 'Media mañana', 'Queso fresco batido con arándanos y nueces', 'Queso fresco batido 0 % 150 g; Arándanos 75 g; Nueces 10 g', 181, 14, 15, 7),
  ('Salud general', 2, 3, 'Comida', 'Merluza con quinoa y brócoli', 'Merluza (peso en crudo) 180 g; Quinoa (peso en crudo) 70 g; Verdura variada (cocinada o salteada) 275 g; Aceite de oliva virgen extra (1 cda., 10 g); 1 pieza de fruta (150 g)', 625, 47, 71, 17),
  ('Salud general', 2, 4, 'Merienda', 'Fruta y puñado de almendras', '1 manzana (150 g); Almendras 20 g', 197, 5, 21, 10),
  ('Salud general', 2, 5, 'Cena', 'Tortilla francesa de 3 huevos con ensalada y pan integral', '3 huevos (150 g); Ensalada (lechuga, tomate, zanahoria…) 225 g; Pan integral (2 rebanadas, 60 g); Aceite de oliva virgen extra (0,5 cda., 5 g)', 447, 27, 35, 22),
  ('Salud general', 3, 1, 'Desayuno', 'Tostadas integrales con huevo, aguacate y naranja', 'Pan integral (2 rebanadas, 60 g); 2 huevos (100 g); Aguacate 40 g; Tomate 80 g; 1 naranja (150 g)', 435, 21, 47, 18),
  ('Salud general', 3, 2, 'Media mañana', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 125 g; Fresas 150 g; Almendras 10 g', 186, 8, 18, 9),
  ('Salud general', 3, 3, 'Comida', 'Pollo a la plancha con arroz integral y verduras salteadas', 'Pechuga de pollo (peso en crudo) 140 g; Arroz integral (peso en crudo) 75 g; Verdura variada (cocinada o salteada) 275 g; Aceite de oliva virgen extra (1 cda., 10 g); 1 pieza de fruta (150 g)', 651, 44, 85, 15),
  ('Salud general', 3, 4, 'Merienda', 'Queso fresco batido con arándanos y nueces', 'Queso fresco batido 0 % 150 g; Arándanos 75 g; Nueces 10 g', 181, 14, 15, 7),
  ('Salud general', 3, 5, 'Cena', 'Salmón a la plancha con calabacín y quinoa', 'Salmón (peso en crudo) 110 g; Quinoa (peso en crudo) 45 g; Verdura variada (cocinada o salteada) 275 g; Aceite de oliva virgen extra (0,5 cda., 5 g)', 493, 34, 38, 23),
  ('Salud general', 4, 1, 'Desayuno', 'Porridge de avena con leche, manzana y crema de cacahuete', 'Copos de avena 50 g; Leche semidesnatada 250 ml; 1 manzana (150 g); Crema de cacahuete 100 % 10 g', 439, 18, 63, 13),
  ('Salud general', 4, 2, 'Media mañana', 'Fruta y puñado de almendras', '1 manzana (150 g); Almendras 20 g', 197, 5, 21, 10),
  ('Salud general', 4, 3, 'Comida', 'Garbanzos con espinacas y pechuga de pavo', 'Garbanzos cocidos 290 g; Pechuga de pavo (peso en crudo) 90 g; Verdura variada (cocinada o salteada) 225 g; Aceite de oliva virgen extra (1 cda., 10 g)', 623, 49, 61, 20),
  ('Salud general', 4, 4, 'Merienda', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 125 g; Fresas 150 g; Almendras 10 g', 186, 8, 18, 9),
  ('Salud general', 4, 5, 'Cena', 'Crema de verduras con tostadas de pavo y queso fresco', 'Verdura variada (cocinada o salteada) 375 g; Pan integral (2 rebanadas, 60 g); Pechuga de pavo en lonchas 70 g; Queso fresco batido 0 % 125 g; Aceite de oliva virgen extra (0,5 cda., 5 g)', 420, 36, 47, 10),
  ('Salud general', 5, 1, 'Desayuno', 'Bol de yogur griego con avena, plátano y nueces', 'Yogur griego natural 150 g; Copos de avena 45 g; 1 plátano (100 g); Nueces 10 g', 462, 22, 54, 17),
  ('Salud general', 5, 2, 'Media mañana', 'Queso fresco batido con arándanos y nueces', 'Queso fresco batido 0 % 150 g; Arándanos 75 g; Nueces 10 g', 181, 14, 15, 7),
  ('Salud general', 5, 3, 'Comida', 'Salmón al horno con patata y ensalada', 'Salmón (peso en crudo) 140 g; Patata (peso en crudo) 260 g; Ensalada (lechuga, tomate, zanahoria…) 225 g; Aceite de oliva virgen extra (0,5 cda., 5 g); 1 pieza de fruta (150 g)', 645, 37, 70, 24),
  ('Salud general', 5, 4, 'Merienda', 'Fruta y puñado de almendras', '1 manzana (150 g); Almendras 20 g', 197, 5, 21, 10),
  ('Salud general', 5, 5, 'Cena', 'Pechuga de pavo con boniato asado y verduras', 'Pechuga de pavo (peso en crudo) 140 g; Boniato (peso en crudo) 210 g; Verdura variada (cocinada o salteada) 275 g; Aceite de oliva virgen extra (1 cda., 10 g)', 491, 42, 53, 12),
  ('Salud general', 6, 1, 'Desayuno', 'Tostadas integrales con huevo, aguacate y naranja', 'Pan integral (2 rebanadas, 60 g); 2 huevos (100 g); Aguacate 40 g; Tomate 80 g; 1 naranja (150 g)', 435, 21, 47, 18),
  ('Salud general', 6, 2, 'Media mañana', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 125 g; Fresas 150 g; Almendras 10 g', 186, 8, 18, 9),
  ('Salud general', 6, 3, 'Comida', 'Arroz con atún, huevo y ensalada', 'Arroz integral (peso en crudo) 75 g; Atún al natural (escurrido) 110 g; 1 huevo (50 g); Ensalada (lechuga, tomate, zanahoria…) 225 g; Aceite de oliva virgen extra (1 cda., 10 g); 1 pieza de fruta (150 g)', 667, 43, 82, 19),
  ('Salud general', 6, 4, 'Merienda', 'Queso fresco batido con arándanos y nueces', 'Queso fresco batido 0 % 150 g; Arándanos 75 g; Nueces 10 g', 181, 14, 15, 7),
  ('Salud general', 6, 5, 'Cena', 'Pollo salteado con verduras y arroz integral', 'Pechuga de pollo (peso en crudo) 140 g; Arroz integral (peso en crudo) 45 g; Verdura variada (cocinada o salteada) 325 g; Aceite de oliva virgen extra (1 cda., 10 g)', 481, 42, 46, 14),
  ('Salud general', 7, 1, 'Desayuno', 'Porridge de avena con leche, manzana y crema de cacahuete', 'Copos de avena 50 g; Leche semidesnatada 250 ml; 1 manzana (150 g); Crema de cacahuete 100 % 10 g', 439, 18, 63, 13),
  ('Salud general', 7, 2, 'Media mañana', 'Fruta y puñado de almendras', '1 manzana (150 g); Almendras 20 g', 197, 5, 21, 10),
  ('Salud general', 7, 3, 'Comida', 'Pasta integral con ternera magra y tomate natural', 'Pasta integral (peso en crudo) 75 g; Ternera magra (peso en crudo) 120 g; Tomate 220 g; Aceite de oliva virgen extra (1 cda., 10 g); Verdura variada (cocinada o salteada) 175 g; 1 pieza de fruta (150 g)', 663, 41, 82, 19),
  ('Salud general', 7, 4, 'Merienda', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 125 g; Fresas 150 g; Almendras 10 g', 186, 8, 18, 9),
  ('Salud general', 7, 5, 'Cena', 'Ensalada completa de atún, huevo y garbanzos', 'Atún al natural (escurrido) 90 g; 1 huevo (50 g); Garbanzos cocidos 130 g; Ensalada (lechuga, tomate, zanahoria…) 275 g; Aceite de oliva virgen extra (1 cda., 10 g)', 486, 42, 33, 20),
  ('Constancia', 1, 1, 'Desayuno', 'Bol de yogur griego con avena, plátano y nueces', 'Yogur griego natural 150 g; Copos de avena 45 g; 1 plátano (100 g); Nueces 10 g', 462, 22, 54, 17),
  ('Constancia', 1, 2, 'Media mañana', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 125 g; Fresas 150 g; Almendras 10 g', 186, 8, 18, 9),
  ('Constancia', 1, 3, 'Comida', 'Pollo a la plancha con arroz integral y verduras salteadas', 'Pechuga de pollo (peso en crudo) 150 g; Arroz integral (peso en crudo) 70 g; Verdura variada (cocinada o salteada) 250 g; Aceite de oliva virgen extra (1 cda., 10 g); 1 pieza de fruta (150 g)', 637, 46, 80, 15),
  ('Constancia', 1, 4, 'Merienda', 'Mini bocadillo de pavo y tomate', 'Pan integral (2 rebanadas, 60 g); Pechuga de pavo en lonchas 40 g; Tomate 60 g', 194, 13, 29, 3),
  ('Constancia', 1, 5, 'Cena', 'Pechuga de pavo con boniato asado y verduras', 'Pechuga de pavo (peso en crudo) 150 g; Boniato (peso en crudo) 200 g; Verdura variada (cocinada o salteada) 250 g; Aceite de oliva virgen extra (1 cda., 10 g)', 486, 43, 50, 12),
  ('Constancia', 2, 1, 'Desayuno', 'Porridge de avena con leche, manzana y crema de cacahuete', 'Copos de avena 50 g; Leche semidesnatada 250 ml; 1 manzana (150 g); Crema de cacahuete 100 % 10 g', 439, 18, 63, 13),
  ('Constancia', 2, 2, 'Media mañana', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 125 g; Fresas 150 g; Almendras 10 g', 186, 8, 18, 9),
  ('Constancia', 2, 3, 'Comida', 'Pollo a la plancha con arroz integral y verduras salteadas', 'Pechuga de pollo (peso en crudo) 150 g; Arroz integral (peso en crudo) 70 g; Verdura variada (cocinada o salteada) 250 g; Aceite de oliva virgen extra (1 cda., 10 g); 1 pieza de fruta (150 g)', 637, 46, 80, 15),
  ('Constancia', 2, 4, 'Merienda', 'Mini bocadillo de pavo y tomate', 'Pan integral (2 rebanadas, 60 g); Pechuga de pavo en lonchas 40 g; Tomate 60 g', 194, 13, 29, 3),
  ('Constancia', 2, 5, 'Cena', 'Pechuga de pavo con boniato asado y verduras', 'Pechuga de pavo (peso en crudo) 150 g; Boniato (peso en crudo) 200 g; Verdura variada (cocinada o salteada) 250 g; Aceite de oliva virgen extra (1 cda., 10 g)', 486, 43, 50, 12),
  ('Constancia', 3, 1, 'Desayuno', 'Bol de yogur griego con avena, plátano y nueces', 'Yogur griego natural 150 g; Copos de avena 45 g; 1 plátano (100 g); Nueces 10 g', 462, 22, 54, 17),
  ('Constancia', 3, 2, 'Media mañana', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 125 g; Fresas 150 g; Almendras 10 g', 186, 8, 18, 9),
  ('Constancia', 3, 3, 'Comida', 'Lentejas estofadas con verduras y huevo duro', 'Lentejas cocidas 300 g; 2 huevos (100 g); Verdura variada (cocinada o salteada) 150 g; Aceite de oliva virgen extra (1 cda., 10 g); 1 pieza de fruta (150 g)', 677, 43, 76, 22),
  ('Constancia', 3, 4, 'Merienda', 'Mini bocadillo de pavo y tomate', 'Pan integral (2 rebanadas, 60 g); Pechuga de pavo en lonchas 40 g; Tomate 60 g', 194, 13, 29, 3),
  ('Constancia', 3, 5, 'Cena', 'Pollo salteado con verduras y arroz integral', 'Pechuga de pollo (peso en crudo) 150 g; Arroz integral (peso en crudo) 45 g; Verdura variada (cocinada o salteada) 300 g; Aceite de oliva virgen extra (1 cda., 10 g)', 485, 44, 45, 14),
  ('Constancia', 4, 1, 'Desayuno', 'Porridge de avena con leche, manzana y crema de cacahuete', 'Copos de avena 50 g; Leche semidesnatada 250 ml; 1 manzana (150 g); Crema de cacahuete 100 % 10 g', 439, 18, 63, 13),
  ('Constancia', 4, 2, 'Media mañana', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 125 g; Fresas 150 g; Almendras 10 g', 186, 8, 18, 9),
  ('Constancia', 4, 3, 'Comida', 'Lentejas estofadas con verduras y huevo duro', 'Lentejas cocidas 300 g; 2 huevos (100 g); Verdura variada (cocinada o salteada) 150 g; Aceite de oliva virgen extra (1 cda., 10 g); 1 pieza de fruta (150 g)', 677, 43, 76, 22),
  ('Constancia', 4, 4, 'Merienda', 'Mini bocadillo de pavo y tomate', 'Pan integral (2 rebanadas, 60 g); Pechuga de pavo en lonchas 40 g; Tomate 60 g', 194, 13, 29, 3),
  ('Constancia', 4, 5, 'Cena', 'Pollo salteado con verduras y arroz integral', 'Pechuga de pollo (peso en crudo) 150 g; Arroz integral (peso en crudo) 45 g; Verdura variada (cocinada o salteada) 300 g; Aceite de oliva virgen extra (1 cda., 10 g)', 485, 44, 45, 14),
  ('Constancia', 5, 1, 'Desayuno', 'Bol de yogur griego con avena, plátano y nueces', 'Yogur griego natural 150 g; Copos de avena 45 g; 1 plátano (100 g); Nueces 10 g', 462, 22, 54, 17),
  ('Constancia', 5, 2, 'Media mañana', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 125 g; Fresas 150 g; Almendras 10 g', 186, 8, 18, 9),
  ('Constancia', 5, 3, 'Comida', 'Salmón al horno con patata y ensalada', 'Salmón (peso en crudo) 150 g; Patata (peso en crudo) 250 g; Ensalada (lechuga, tomate, zanahoria…) 200 g; Aceite de oliva virgen extra (0,5 cda., 5 g); 1 pieza de fruta (150 g)', 652, 38, 68, 25),
  ('Constancia', 5, 4, 'Merienda', 'Mini bocadillo de pavo y tomate', 'Pan integral (2 rebanadas, 60 g); Pechuga de pavo en lonchas 40 g; Tomate 60 g', 194, 13, 29, 3),
  ('Constancia', 5, 5, 'Cena', 'Tortilla francesa de 3 huevos con ensalada y pan integral', '3 huevos (150 g); Ensalada (lechuga, tomate, zanahoria…) 200 g; Pan integral (2 rebanadas, 60 g); Aceite de oliva virgen extra (0,5 cda., 5 g)', 441, 27, 34, 22),
  ('Constancia', 6, 1, 'Desayuno', 'Porridge de avena con leche, manzana y crema de cacahuete', 'Copos de avena 50 g; Leche semidesnatada 250 ml; 1 manzana (150 g); Crema de cacahuete 100 % 10 g', 439, 18, 63, 13),
  ('Constancia', 6, 2, 'Media mañana', 'Yogur natural con fresas y almendras', 'Yogur natural sin azúcar 125 g; Fresas 150 g; Almendras 10 g', 186, 8, 18, 9),
  ('Constancia', 6, 3, 'Comida', 'Salmón al horno con patata y ensalada', 'Salmón (peso en crudo) 150 g; Patata (peso en crudo) 250 g; Ensalada (lechuga, tomate, zanahoria…) 200 g; Aceite de oliva virgen extra (0,5 cda., 5 g); 1 pieza de fruta (150 g)', 652, 38, 68, 25),
  ('Constancia', 6, 4, 'Merienda', 'Mini bocadillo de pavo y tomate', 'Pan integral (2 rebanadas, 60 g); Pechuga de pavo en lonchas 40 g; Tomate 60 g', 194, 13, 29, 3),
  ('Constancia', 6, 5, 'Cena', 'Tortilla francesa de 3 huevos con ensalada y pan integral', '3 huevos (150 g); Ensalada (lechuga, tomate, zanahoria…) 200 g; Pan integral (2 rebanadas, 60 g); Aceite de oliva virgen extra (0,5 cda., 5 g)', 441, 27, 34, 22),
  ('Constancia', 7, 1, 'Desayuno', 'Tostadas integrales con huevo, aguacate y naranja', 'Pan integral (2 rebanadas, 60 g); 2 huevos (100 g); Aguacate 40 g; Tomate 80 g; 1 naranja (150 g)', 435, 21, 47, 18),
  ('Constancia', 7, 2, 'Media mañana', 'Fruta y puñado de almendras', '1 manzana (150 g); Almendras 20 g', 197, 5, 21, 10),
  ('Constancia', 7, 3, 'Comida', 'Arroz con atún, huevo y ensalada', 'Arroz integral (peso en crudo) 70 g; Atún al natural (escurrido) 120 g; 1 huevo (50 g); Ensalada (lechuga, tomate, zanahoria…) 200 g; Aceite de oliva virgen extra (1 cda., 10 g); 1 pieza de fruta (150 g)', 656, 45, 77, 19),
  ('Constancia', 7, 4, 'Merienda', 'Queso fresco batido con arándanos y nueces', 'Queso fresco batido 0 % 150 g; Arándanos 75 g; Nueces 10 g', 181, 14, 15, 7),
  ('Constancia', 7, 5, 'Cena', 'Crema de verduras con tostadas de pavo y queso fresco', 'Verdura variada (cocinada o salteada) 350 g; Pan integral (2 rebanadas, 60 g); Pechuga de pavo en lonchas 80 g; Queso fresco batido 0 % 125 g; Aceite de oliva virgen extra (0,5 cda., 5 g)', 424, 37, 46, 10)
on conflict (objetivo, dia, orden) do update set
  toma = excluded.toma, plato = excluded.plato, ingredientes = excluded.ingredientes,
  kcal = excluded.kcal, proteinas = excluded.proteinas, hidratos = excluded.hidratos,
  grasas = excluded.grasas;


-- 4. Seguridad: solo Premium las puede leer (RLS) ---------------------------------
-- Nadie puede cambiarlas desde la web todavía: el equipo las cambia en Supabase
-- (Table Editor) hasta que exista el panel de administración (PVBPQAE-95).
alter table alimentacion enable row level security;
alter table menus_alimentacion enable row level security;

drop policy if exists "leer la alimentacion si soy premium" on alimentacion;
create policy "leer la alimentacion si soy premium" on alimentacion
  for select to authenticated
  using (exists (select 1 from "Registro de usuarios" r
                 where r.auth_id = auth.uid() and r.plan = 'Premium'));

drop policy if exists "leer los menus si soy premium" on menus_alimentacion;
create policy "leer los menus si soy premium" on menus_alimentacion
  for select to authenticated
  using (exists (select 1 from "Registro de usuarios" r
                 where r.auth_id = auth.uid() and r.plan = 'Premium'));
