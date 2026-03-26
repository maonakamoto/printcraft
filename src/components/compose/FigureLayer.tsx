'use client'

import { useRef, useEffect, useState } from 'react'
import { Image as KonvaImage, Transformer } from 'react-konva'
import type Konva from 'konva'
import type { Figure } from '@/types/database'

interface FigureLayerProps {
  figure: Figure
  imageUrl: string
  canvasWidth: number
  canvasHeight: number
  totalWidthCm: number
  totalHeightCm: number
  isSelected: boolean
  onSelect: () => void
  onDragEnd: (figureId: string, x: number, y: number) => void
  onScaleChange: (figureId: string, scale: number) => void
}

export function FigureLayer({
  figure,
  imageUrl,
  canvasWidth,
  canvasHeight,
  totalWidthCm,
  totalHeightCm,
  isSelected,
  onSelect,
  onDragEnd,
  onScaleChange,
}: FigureLayerProps) {
  const imageRef = useRef<Konva.Image>(null)
  const trRef = useRef<Konva.Transformer>(null)
  const [image, setImage] = useState<HTMLImageElement | null>(null)

  useEffect(() => {
    const img = new window.Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => setImage(img)
    img.src = imageUrl
  }, [imageUrl])

  useEffect(() => {
    if (isSelected && trRef.current && imageRef.current) {
      trRef.current.nodes([imageRef.current])
      trRef.current.getLayer()?.batchDraw()
    }
  }, [isSelected])

  if (!image) return null

  // Position: normalized (0-1) -> canvas pixels
  const x = (figure.position_x ?? 0.5) * canvasWidth
  const y = (figure.position_y ?? 0.5) * canvasHeight

  // Scale figure to reasonable size relative to canvas
  const baseScale = Math.min(canvasWidth / image.width, canvasHeight / image.height) * 0.3
  const figScale = baseScale * figure.scale

  return (
    <>
      <KonvaImage
        ref={imageRef}
        image={image}
        x={x}
        y={y}
        scaleX={figScale}
        scaleY={figScale}
        offsetX={image.width / 2}
        offsetY={image.height / 2}
        draggable
        onClick={onSelect}
        onTap={onSelect}
        onDragEnd={(e) => {
          const node = e.target
          const normX = (node.x() / canvasWidth) * totalWidthCm
          const normY = (node.y() / canvasHeight) * totalHeightCm
          onDragEnd(figure.id, normX, normY)
        }}
        onTransformEnd={() => {
          const node = imageRef.current
          if (!node) return
          const newScaleX = node.scaleX()
          const relativeScale = newScaleX / baseScale
          node.scaleX(newScaleX)
          node.scaleY(newScaleX)
          onScaleChange(figure.id, relativeScale)
        }}
      />
      {isSelected && (
        <Transformer
          ref={trRef}
          enabledAnchors={['top-left', 'top-right', 'bottom-left', 'bottom-right']}
          keepRatio={true}
          boundBoxFunc={(oldBox, newBox) => {
            if (newBox.width < 20 || newBox.height < 20) return oldBox
            return newBox
          }}
        />
      )}
    </>
  )
}
