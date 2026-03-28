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
      // Export at max quality — 4x gives ~3200x2400 from an 800px canvas
      // For full print DPI, use the Export page (Phase 2)
      const dataUrl = stage.toDataURL({ pixelRatio: 4 })
      const link = document.createElement('a')
      link.download = `printcraft-composition.png`
      link.href = dataUrl
      link.click()
      toast.success('PNG exported (4x resolution)')
    } catch (err) {
      // Canvas size limit hit — fall back to 2x
      try {
        const dataUrl = stageRef.current!.toDataURL({ pixelRatio: 2 })
        const link = document.createElement('a')
        link.download = `printcraft-composition.png`
        link.href = dataUrl
        link.click()
        toast.success('PNG exported (2x resolution)')
      } catch {
        toast.error('Export failed — try a smaller canvas')
      }
    }
  }

  function handleBgFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) onBackgroundUpload(file)
  }

  return (
    <div className="flex items-center gap-3 px-5 py-3 rounded-xl glass border border-white/[0.06] flex-wrap">
      <Button variant="outline" size="sm" disabled={!selectedId} onClick={() => moveLayer('up')}>
        <ArrowUp className="h-4 w-4 mr-1.5" /> Forward
      </Button>
      <Button variant="outline" size="sm" disabled={!selectedId} onClick={() => moveLayer('down')}>
        <ArrowDown className="h-4 w-4 mr-1.5" /> Back
      </Button>

      <Separator orientation="vertical" className="h-6" />

      <Button variant="outline" size="sm" onClick={() => bgInputRef.current?.click()}>
        <ImagePlus className="h-4 w-4 mr-1.5" /> Background
      </Button>
      <input ref={bgInputRef} type="file" className="hidden" accept="image/*" onChange={handleBgFileChange} />

      <Button variant="default" size="sm" onClick={handleExportPng}>
        <Download className="h-4 w-4 mr-1.5" /> Export PNG
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
