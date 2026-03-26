'use client'

import { useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { ArrowUp, ArrowDown, Upload } from 'lucide-react'
import { useUpdateFigure } from '@/hooks/useFigures'
import { useSupabaseUpload } from '@/hooks/useSupabaseUpload'
import { toast } from 'sonner'
import type { Figure } from '@/types/database'
import type Konva from 'konva'

interface CanvasToolbarProps {
  stageRef: React.RefObject<Konva.Stage | null>
  selectedId: string | null
  figures: Figure[]
  projectId: string
}

export function CanvasToolbar({ stageRef, selectedId, figures, projectId }: CanvasToolbarProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const updateFigure = useUpdateFigure(projectId)

  const selectedFigure = figures.find(f => f.id === selectedId)

  function moveLayer(direction: 'up' | 'down') {
    if (!selectedFigure) return
    const newDepth = direction === 'up' ? selectedFigure.z_depth + 1 : Math.max(0, selectedFigure.z_depth - 1)
    updateFigure.mutate({ id: selectedFigure.id, data: { z_depth: newDepth } })
  }

  return (
    <div className="flex items-center gap-2 px-2">
      <Button
        variant="outline"
        size="sm"
        disabled={!selectedId}
        onClick={() => moveLayer('up')}
      >
        <ArrowUp className="h-3 w-3 mr-1" /> Forward
      </Button>
      <Button
        variant="outline"
        size="sm"
        disabled={!selectedId}
        onClick={() => moveLayer('down')}
      >
        <ArrowDown className="h-3 w-3 mr-1" /> Back
      </Button>

      <Separator orientation="vertical" className="h-6" />

      {selectedFigure && (
        <span className="text-xs text-muted-foreground">
          {selectedFigure.label ?? 'Unnamed figure'}
        </span>
      )}
    </div>
  )
}
