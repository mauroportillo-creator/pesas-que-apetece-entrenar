import { createClient } from '@supabase/supabase-js'

const url = import.meta.env.VITE_SUPABASE_URL
const key = import.meta.env.VITE_SUPABASE_KEY

// true si las variables de entorno están rellenas (ver .env.example)
export const configurado = Boolean(url && key)

export const supabase = configurado ? createClient(url, key) : null
