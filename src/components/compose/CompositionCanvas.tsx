'use client'

import { useRef, useState, useEffect, useCallback } from 'react'
import { Stage, Layer, Rect, Line } from 'react-konva'
import { FigureLayer } from './FigureLayer'
import { CanvasToolbar } from './CanvasToolbar'
import { getTotalDimensions } from '@/lib/domain/surface'
import { useUpdateFigure } from '@/hooks/useFigures'
import { getImageUrl } from '@/lib/supabase/storage'
import type { Figure, Surface } from '@/types/database'
import type Konva from 'konva'

interface CompositionCanvasProps {
  projectId: string
  figures: Figure[]
  surface: Surface
}

export function CompositionCanvas({ projectId, figures, surface }: CompositionCanvasProps) {
  const stageRef = useRef<Konva.Stage>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [containerSize, setContainerSize] = useState({ width: 800, height: 600 })
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [bgImage, setBgImage] = useState<HTMLImageElement | null>(null)
  const updateFigure = useUpdateFigure(projectId)

  const { width_cm, height_cm } = getTotalDimensions(surface.panels)
  const aspectRatio = width_cm / height_cm

  // Fit canvas to container
  useEffect(() => {
    function resize() {
      if (!containerRef.current) return
      const w = containerRef.current.clientWidth
      const h = Math.min(w / aspectRatio, window.innerHeight - 200)
      setContainerSize({ width: w, height: h })
    }
    resize()
    window.addEventListener('resize', resize)
    return () => window.removeEventListener('resize', resize)
  }, [aspectRatio])

  // Build image URLs (synchronous — public bucket)
  const imageUrls: Record<string, string> = {}
  for (const fig of figures) {
    const path = fig.styled_url || fig.original_photo_url
    if (path) imageUrls[fig.id] = getImageUrl(path)
  }

  const handleDragEnd = useCallback((figureId: string, normX: number, normY: number) => {
    updateFigure.mutate({ id: figureId, data: { position_x: normX, position_y: normY } })
  }, [updateFigure])

  const handleScaleChange = useCallback((figureId: string, scale: number) => {
    updateFigure.mutate({ id: figureId, data: { scale } })
  }, [updateFigure])

  return (
    <div className="flex flex-col gap-3">
      <CanvasToolbar
        stageRef={stageRef}
        selectedId={selectedId}
        figures={figures}
        projectId={projectId}
        onBackgroundUpload={(file) => {
          const url = URL.createObjectURL(file)
          const img = new window.Image()
          img.onload = () => setBgImage(img)
          img.src = url
        }}
      />
      <div
        ref={containerRef}
        className="border border-border rounded-lg overflow-hidden bg-black"
      >
        <Stage
          ref={stageRef}
          width={containerSize.width}
          height={containerSize.height}
          onClick={(e) => {
            if (e.target === e.target.getStage()) setSelectedId(null)
          }}
        >
          {/* Background */}
          <Layer>
            <Rect
              width={containerSize.width}
              height={containerSize.height}
              fill="#111"
            />
            {bgImage && (
              <Rect
                width={containerSize.width}
                height={containerSize.height}
                fillPatternImage={bgImage}
                fillPatternScaleX={containerSize.width / bgImage.width}
                fillPatternScaleY={containerSize.height / bgImage.height}
              />
            )}
          </Layer>

          {/* Figures */}
          <Layer>
            {figures
              .filter(f => imageUrls[f.id])
              .sort((a, b) => a.z_depth - b.z_depth)
              .map(figure => (
                <FigureLayer
                  key={figure.id}
                  figure={figure}
                  imageUrl={imageUrls[figure.id]}
                  canvasWidth={containerSize.width}
                  canvasHeight={containerSize.height}
                  totalWidthCm={width_cm}
                  totalHeightCm={height_cm}
                  isSelected={selectedId === figure.id}
                  onSelect={() => setSelectedId(figure.id)}
                  onDragEnd={handleDragEnd}
                  onScaleChange={handleScaleChange}
                />
              ))}
          </Layer>

          {/* Constraint overlays */}
          <Layer listening={false}>
            {/* Seam lines */}
            {surface.seam_positions.map((seam, i) => {
              const x = (seam.x_cm / width_cm) * containerSize.width
              return (
                <Line
                  key={`seam-${i}`}
                  points={[x, 0, x, containerSize.height]}
                  stroke="rgba(255,100,100,0.6)"
                  strokeWidth={2}
                  dash={[8, 4]}
                />
              )
            })}

            {/* Dead zones */}
            {surface.dead_zones.map((zone, i) => {
              const x = (zone.x_cm / width_cm) * containerSize.width
              const y = containerSize.height - ((zone.y_cm + zone.height_cm) / height_cm) * containerSize.height
              const w = (zone.width_cm / width_cm) * containerSize.width
              const h = (zone.height_cm / height_cm) * containerSize.height
              return (
                <Rect
                  key={`dead-${i}`}
                  x={x}
                  y={y}
                  width={w}
                  height={h}
                  fill="rgba(255,50,50,0.15)"
                  stroke="rgba(255,50,50,0.5)"
                  strokeWidth={1}
                  dash={[4, 2]}
                />
              )
            })}

            {/* Seam buffer zones */}
            {surface.seam_positions.map((seam, i) => {
              const bufferCm = 10
              const x = ((seam.x_cm - bufferCm) / width_cm) * containerSize.width
              const w = (bufferCm * 2 / width_cm) * containerSize.width
              return (
                <Rect
                  key={`buffer-${i}`}
                  x={x}
                  y={0}
                  width={w}
                  height={containerSize.height}
                  fill="rgba(255,100,100,0.05)"
                />
              )
            })}
          </Layer>
        </Stage>
      </div>
    </div>
  )
}
