'use client'

import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload } from 'lucide-react'
import { useSupabaseUpload } from '@/hooks/useSupabaseUpload'
import { useCreateFigure } from '@/hooks/useFigures'
import { toast } from 'sonner'

interface FigureUploaderProps {
  projectId: string
}

export function FigureUploader({ projectId }: FigureUploaderProps) {
  const { upload, uploading } = useSupabaseUpload(projectId)
  const createFigure = useCreateFigure()

  const onDrop = useCallback(async (files: File[]) => {
    for (const file of files) {
      const result = await upload(file, 'originals')
      if (!result) {
        toast.error(`Failed to upload ${file.name}`)
        continue
      }

      createFigure.mutate(
        {
          project_id: projectId,
          original_photo_url: result.path,
          label: file.name.replace(/\.[^/.]+$/, ''),
        },
        {
          onError: (err) => toast.error(err.message),
        }
      )
    }
  }, [upload, createFigure, projectId])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.webp'] },
    disabled: uploading,
  })

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors
        ${isDragActive ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'}
        ${uploading ? 'opacity-50 cursor-wait' : ''}
      `}
    >
      <input {...getInputProps()} />
      <Upload className="h-8 w-8 mx-auto mb-3 text-muted-foreground" />
      <p className="text-sm font-medium">
        {uploading ? 'Uploading...' : isDragActive ? 'Drop photos here' : 'Drop photos or click to upload'}
      </p>
      <p className="text-xs text-muted-foreground mt-1">
        PNG, JPG, WEBP — one photo per person or group
      </p>
    </div>
  )
}
