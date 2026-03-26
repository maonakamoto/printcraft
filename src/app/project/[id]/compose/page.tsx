'use client'

import { use } from 'react'
import dynamic from 'next/dynamic'
import { useFigures } from '@/hooks/useFigures'
import { useSurface } from '@/hooks/useSurface'
import { Skeleton } from '@/components/ui/skeleton'

const CompositionCanvas = dynamic(
  () => import('@/components/compose/CompositionCanvas').then(m => ({ default: m.CompositionCanvas })),
  { ssr: false, loading: () => <Skeleton className="h-[500px] rounded-xl" /> }
)

export default function ComposePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const { data: figures, isLoading: figuresLoading } = useFigures(id)
  const { data: surface, isLoading: surfaceLoading } = useSurface(id)

  const isLoading = figuresLoading || surfaceLoading

  if (isLoading) {
    return (
      <div className="p-6">
        <Skeleton className="h-[500px] rounded-xl" />
      </div>
    )
  }

  if (!surface) {
    return (
      <div className="p-6 max-w-3xl mx-auto text-center py-20">
        <h2 className="text-lg font-medium mb-1">No surface defined</h2>
        <p className="text-sm text-muted-foreground">
          Define your physical surface first before composing.
        </p>
      </div>
    )
  }

  const styledFigures = figures?.filter(f => f.styled_url || f.original_photo_url) ?? []

  if (styledFigures.length === 0) {
    return (
      <div className="p-6 max-w-3xl mx-auto text-center py-20">
        <h2 className="text-lg font-medium mb-1">No figures to compose</h2>
        <p className="text-sm text-muted-foreground">
          Upload photos and their styled versions first.
        </p>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-4">
      <div>
        <h2 className="text-xl font-bold tracking-tight">Compose</h2>
        <p className="text-sm text-muted-foreground">
          Drag figures into position. Red dashed lines show panel seams. Red zones are dead zones.
        </p>
      </div>
      <CompositionCanvas
        projectId={id}
        figures={styledFigures}
        surface={surface}
      />
    </div>
  )
}
