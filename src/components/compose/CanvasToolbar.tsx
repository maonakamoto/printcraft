'use client'

import { useRef } from 'react'
import { Button } from '@/components/ui/button'
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
      const dataUrl = stage.toDataURL({ pixelRatio: 4 })
      const link = document.createElement('a')
      link.download = `printcraft-composition.png`
      link.href = dataUrl
      link.click()
      toast.success('PNG exported (4x resolution)')
    } catch {
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
    <div className="inline-flex items-center gap-1.5 sm:gap-2 px-3 sm:px-5 py-2.5 sm:py-3 rounded-2xl glass-strong border border-white/[0.06] shadow-xl shadow-black/20 flex-wrap justify-center">
      <Button variant="outline" size="sm" className="rounded-full h-8 text-xs sm:text-sm" disabled={!selectedId} onClick={() => moveLayer('up')}>
        <ArrowUp className="h-3.5 w-3.5 sm:mr-1.5" />
        <span className="hidden sm:inline">Forward</span>
      </Button>
      <Button variant="outline" size="sm" className="rounded-full h-8 text-xs sm:text-sm" disabled={!selectedId} onClick={() => moveLayer('down')}>
        <ArrowDown className="h-3.5 w-3.5 sm:mr-1.5" />
        <span className="hidden sm:inline">Back</span>
      </Button>

      <div className="h-5 w-px bg-white/[0.08] mx-0.5 sm:mx-1" />

      <Button variant="outline" size="sm" className="rounded-full h-8 text-xs sm:text-sm" onClick={() => bgInputRef.current?.click()}>
        <ImagePlus className="h-3.5 w-3.5 sm:mr-1.5" />
        <span className="hidden sm:inline">Background</span>
      </Button>
      <input ref={bgInputRef} type="file" className="hidden" accept="image/*" onChange={handleBgFileChange} />

      <Button variant="default" size="sm" className="rounded-full h-8 text-xs sm:text-sm" onClick={handleExportPng}>
        <Download className="h-3.5 w-3.5 sm:mr-1.5" />
        <span className="hidden sm:inline">Export PNG</span>
      </Button>

      {selectedFigure && (
        <>
          <div className="h-5 w-px bg-white/[0.08] mx-0.5 sm:mx-1 hidden sm:block" />
          <span className="text-xs text-muted-foreground hidden sm:inline">
            {selectedFigure.label ?? 'Unnamed figure'}
          </span>
        </>
      )}
    </div>
  )
}
