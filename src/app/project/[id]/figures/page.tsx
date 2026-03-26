'use client'

import { use } from 'react'
import { useFigures } from '@/hooks/useFigures'
import { FigureUploader } from '@/components/figures/FigureUploader'
import { FigureCard } from '@/components/figures/FigureCard'
import { Skeleton } from '@/components/ui/skeleton'

export default function FiguresPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const { data: figures, isLoading } = useFigures(id)

  return (
    <div className="p-6 max-w-3xl mx-auto w-full space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight">Figures</h2>
        <p className="text-sm text-muted-foreground">
          Upload photos of the people for your artwork. Then upload the styled version of each.
        </p>
      </div>

      <FigureUploader projectId={id} />

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => <Skeleton key={i} className="h-28 rounded-xl" />)}
        </div>
      ) : figures?.length ? (
        <div className="space-y-3">
          {figures.map(figure => (
            <FigureCard key={figure.id} figure={figure} projectId={id} />
          ))}
        </div>
      ) : null}
    </div>
  )
}
