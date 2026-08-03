import { createClient } from '@supabase/supabase-js'

// Service role client — bypasses RLS. Use only on the server.
export function createAdminClient() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  )
}

// Re-export for server-side code that already imports from here
export { GUEST_USER_ID } from '@/lib/constants'
