import { createClient } from '@supabase/supabase-js'
import { DB_SCHEMA } from './schema'

// Service role client — bypasses RLS. Use only on the server.
export function createAdminClient() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!,
    { db: { schema: DB_SCHEMA } }
  )
}

// Re-export for server-side code that already imports from here
export { GUEST_USER_ID } from '@/lib/constants'
