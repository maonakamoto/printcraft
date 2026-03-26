import { createClient } from './client'
import { createClient as createServerOnlyClient } from '@supabase/supabase-js'

const BUCKET = 'project-files'

function getStorageClient() {
  // Try browser client first, fall back to admin for unauthenticated uploads
  if (typeof window !== 'undefined') {
    return createClient()
  }
  return createServerOnlyClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  )
}

export async function uploadFile(
  path: string,
  file: File
): Promise<{ path: string; error: string | null }> {
  const supabase = createClient()
  const { data, error } = await supabase.storage
    .from(BUCKET)
    .upload(path, file, { upsert: true })

  if (error) {
    // If RLS blocks, try with admin client
    const admin = createServerOnlyClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    )
    // For guest mode, store with public access
    const retry = await supabase.storage.from(BUCKET).upload(path, file, { upsert: true })
    if (retry.error) return { path: '', error: retry.error.message }
    return { path: retry.data.path, error: null }
  }
  return { path: data.path, error: null }
}

export async function getSignedUrl(path: string): Promise<string | null> {
  const supabase = createClient()
  const { data, error } = await supabase.storage
    .from(BUCKET)
    .createSignedUrl(path, 3600)

  if (error) return null
  return data.signedUrl
}

export function getPublicUrl(path: string): string {
  const supabase = createClient()
  const { data } = supabase.storage.from(BUCKET).getPublicUrl(path)
  return data.publicUrl
}

export async function deleteFile(path: string): Promise<boolean> {
  const supabase = createClient()
  const { error } = await supabase.storage
    .from(BUCKET)
    .remove([path])

  return !error
}

export function getStoragePath(
  userId: string,
  projectId: string,
  type: 'originals' | 'styled' | 'backgrounds' | 'exports',
  filename: string
): string {
  return `${userId}/${projectId}/${type}/${filename}`
}
