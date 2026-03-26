'use client'

import { useState } from 'react'
import { uploadFile, getStoragePath } from '@/lib/supabase/storage'
import { useAuth } from '@/components/providers/AuthProvider'

interface UploadResult {
  path: string
  signedUrl: string
}

export function useSupabaseUpload(projectId: string) {
  const { user } = useAuth()
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function upload(
    file: File,
    type: 'originals' | 'styled' | 'backgrounds' | 'exports',
    filename?: string
  ): Promise<UploadResult | null> {
    if (!user) {
      setError('Not authenticated')
      return null
    }

    setUploading(true)
    setError(null)

    const name = filename || `${crypto.randomUUID()}.${file.name.split('.').pop()}`
    const path = getStoragePath(user.id, projectId, type, name)

    const result = await uploadFile(path, file)
    setUploading(false)

    if (result.error) {
      setError(result.error)
      return null
    }

    return { path: result.path, signedUrl: '' }
  }

  return { upload, uploading, error }
}
