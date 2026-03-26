'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Trash2, Upload, Check } from 'lucide-react'
import { getSignedUrl } from '@/lib/supabase/storage'
import { useUpdateFigure, useDeleteFigure } from '@/hooks/useFigures'
import { useSupabaseUpload } from '@/hooks/useSupabaseUpload'
import { toast } from 'sonner'
import type { Figure } from '@/types/database'

interface FigureCardProps {
  figure: Figure
  projectId: string
}

export function FigureCard({ figure, projectId }: FigureCardProps) {
  const [label, setLabel] = useState(figure.label ?? '')
  const [originalUrl, setOriginalUrl] = useState<string | null>(null)
  const [styledUrl, setStyledUrl] = useState<string | null>(null)
  const updateFigure = useUpdateFigure(projectId)
  const deleteFigure = useDeleteFigure(projectId)
  const { upload, uploading } = useSupabaseUpload(projectId)

  useEffect(() => {
    getSignedUrl(figure.original_photo_url).then(setOriginalUrl)
    if (figure.styled_url) {
      getSignedUrl(figure.styled_url).then(setStyledUrl)
    }
  }, [figure.original_photo_url, figure.styled_url])

  function handleLabelBlur() {
    if (label !== (figure.label ?? '')) {
      updateFigure.mutate({ id: figure.id, data: { label: label || null } })
    }
  }

  async function handleStyledUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return

    const result = await upload(file, 'styled')
    if (!result) {
      toast.error('Upload failed')
      return
    }

    updateFigure.mutate(
      { id: figure.id, data: { styled_url: result.path, status: 'styled' } },
      { onSuccess: () => toast.success('Styled version uploaded') }
    )
  }

  function handleDelete() {
    if (!confirm('Delete this figure?')) return
    deleteFigure.mutate(figure.id)
  }

  return (
    <Card className="overflow-hidden">
      <CardContent className="p-3">
        <div className="flex gap-3">
          {/* Original photo */}
          <div className="w-24 h-24 rounded-lg overflow-hidden bg-muted flex-shrink-0">
            {originalUrl && (
              <img src={originalUrl} alt={figure.label ?? 'Figure'} className="w-full h-full object-cover" />
            )}
          </div>

          {/* Styled version */}
          <div className="w-24 h-24 rounded-lg overflow-hidden bg-muted flex-shrink-0 relative group">
            {styledUrl ? (
              <>
                <img src={styledUrl} alt="Styled" className="w-full h-full object-cover" />
                <Badge className="absolute bottom-1 left-1 text-[10px]" variant="secondary">
                  <Check className="h-3 w-3 mr-0.5" /> Styled
                </Badge>
              </>
            ) : (
              <label className="flex flex-col items-center justify-center w-full h-full cursor-pointer hover:bg-muted/80 transition-colors">
                <Upload className="h-4 w-4 text-muted-foreground mb-1" />
                <span className="text-[10px] text-muted-foreground">
                  {uploading ? 'Uploading...' : 'Upload styled'}
                </span>
                <input type="file" className="hidden" accept="image/*" onChange={handleStyledUpload} disabled={uploading} />
              </label>
            )}
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0 flex flex-col justify-between">
            <Input
              value={label}
              onChange={e => setLabel(e.target.value)}
              onBlur={handleLabelBlur}
              placeholder="Label (e.g., Roli + girlfriend)"
              className="h-8 text-sm"
            />
            <div className="flex items-center justify-between mt-2">
              <Badge variant="outline" className="text-xs">
                {figure.status}
              </Badge>
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={handleDelete}>
                <Trash2 className="h-3.5 w-3.5 text-destructive" />
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
