/**
 * PrintCraft's tables live in a dedicated Postgres schema on the shared
 * self-hosted Supabase stack (supabase.orangecat.ch), not in `public` —
 * several apps share that database. Every client must select it explicitly.
 */
export const DB_SCHEMA = 'printcraft'
