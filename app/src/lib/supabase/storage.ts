import { createClient } from './client'

const BUCKET = 'project-files'

export async function uploadFile(
  path: string,
  file: File
): Promise<{ path: string; error: string | null }> {
  const supabase = createClient()
  const { data, error } = await supabase.storage
    .from(BUCKET)
    .upload(path, file, { upsert: true })

  if (error) return { path: '', error: error.message }
  return { path: data.path, error: null }
}

/** Public URL — works because the bucket is public. No auth needed. */
export function getImageUrl(path: string): string {
  return `${process.env.NEXT_PUBLIC_SUPABASE_URL}/storage/v1/object/public/${BUCKET}/${path}`
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
