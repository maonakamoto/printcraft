'use client'

import { useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { ArrowUp, ArrowDown, Download, ImagePlus } from 'lucide-react'
import { useUpdateFigure } from '@/hooks/useFigures'
import { toast } from 'sonner'
import type { Figure } from '@/types/database'
import type Konva from 'konva'

interface CanvasToolbarProps {
  stageRef: React.RefObject<Konva.Stage | null>
  selectedId: string | null
  figures: Figure[]
  projectId: string
  onBackgroundUpload: (file: File) => void
}

export function CanvasToolbar({ stageRef, selectedId, figures, projectId, onBackgroundUpload }: CanvasToolbarProps) {
  const bgInputRef = useRef<HTMLInputElement>(null)
  const updateFigure = useUpdateFigure(projectId)
  const selectedFigure = figures.find(f => f.id === selectedId)

  function moveLayer(direction: 'up' | 'down') {
    if (!selectedFigure) return
    const newDepth = direction === 'up' ? selectedFigure.z_depth + 1 : Math.max(0, selectedFigure.z_depth - 1)
    updateFigure.mutate({ id: selectedFigure.id, data: { z_depth: newDepth } })
  }

  function handleExportPng() {
    const stage = stageRef.current
    if (!stage) return
    try {
      const dataUrl = stage.toDataURL({ pixelRatio: 2 })
      const link = document.createElement('a')
      link.download = `printcraft-composition.png`
      link.href = dataUrl
      link.click()
      toast.success('PNG exported')
    } catch (err) {
      toast.error('Export failed — images may be cross-origin')
    }
  }

  function handleBgFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) onBackgroundUpload(file)
  }

  return (
    <div className="flex items-center gap-2 px-2 flex-wrap">
      <Button variant="outline" size="sm" disabled={!selectedId} onClick={() => moveLayer('up')}>
        <ArrowUp className="h-3 w-3 mr-1" /> Forward
      </Button>
      <Button variant="outline" size="sm" disabled={!selectedId} onClick={() => moveLayer('down')}>
        <ArrowDown className="h-3 w-3 mr-1" /> Back
      </Button>

      <Separator orientation="vertical" className="h-6" />

      <Button variant="outline" size="sm" onClick={() => bgInputRef.current?.click()}>
        <ImagePlus className="h-3 w-3 mr-1" /> Background
      </Button>
      <input ref={bgInputRef} type="file" className="hidden" accept="image/*" onChange={handleBgFileChange} />

      <Button variant="outline" size="sm" onClick={handleExportPng}>
        <Download className="h-3 w-3 mr-1" /> Export PNG
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
