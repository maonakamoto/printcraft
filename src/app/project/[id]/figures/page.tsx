'use client'

import { use } from 'react'
import Link from 'next/link'
import { useFigures } from '@/hooks/useFigures'
import { FigureUploader } from '@/components/figures/FigureUploader'
import { FigureCard } from '@/components/figures/FigureCard'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { ArrowRight, Info } from 'lucide-react'

export default function FiguresPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const { data: figures, isLoading } = useFigures(id)

  const hasStyledFigures = figures?.some(f => f.styled_url)

  return (
    <div className="p-6 max-w-3xl mx-auto w-full space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight">Figures</h2>
        <p className="text-sm text-muted-foreground">
          Upload photos of the people for your artwork.
        </p>
      </div>

      <FigureUploader projectId={id} />

      {/* Phase 1 workflow explanation */}
      <Card className="border-blue-500/20 bg-blue-500/5">
        <CardContent className="p-4 flex gap-3">
          <Info className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-muted-foreground space-y-1">
            <p className="font-medium text-foreground">How it works (Phase 1)</p>
            <ol className="list-decimal list-inside space-y-0.5 text-xs">
              <li>Upload the original photo of each person/group</li>
              <li>Choose an art style in the next step</li>
              <li>Use an AI tool (e.g., Grok, Midjourney) to generate a styled cartoon version</li>
              <li>Upload the styled version here using the &quot;Upload styled&quot; button on each card</li>
              <li>Compose all styled figures together in the canvas editor</li>
            </ol>
          </div>
        </CardContent>
      </Card>

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
      ) : (
        <p className="text-sm text-muted-foreground text-center py-4">
          No figures yet. Drop photos above to get started.
        </p>
      )}

      {figures && figures.length > 0 && (
        <div className="flex justify-end pt-2">
          <Link href={`/project/${id}/style`}>
            <Button>
              Continue to Style <ArrowRight className="h-4 w-4 ml-1" />
            </Button>
          </Link>
        </div>
      )}
    </div>
  )
}
