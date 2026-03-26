import { createClient } from '@supabase/supabase-js'

// Service role client — bypasses RLS. Use only on the server.
export function createAdminClient() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  )
}

// Default guest user ID for unauthenticated access
export const GUEST_USER_ID = '00000000-0000-0000-0000-000000000000'
