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

  return (
    <div className="p-8 max-w-4xl mx-auto w-full space-y-8">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Figures</h2>
        <p className="text-base text-muted-foreground mt-1">
          Upload photos of the people for your artwork.
        </p>
      </div>

      <FigureUploader projectId={id} />

      <Card className="border-primary/20 bg-primary/5">
        <CardContent className="p-5 flex gap-4">
          <Info className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
          <div className="space-y-2">
            <p className="font-medium">How it works</p>
            <ol className="list-decimal list-inside space-y-1 text-sm text-muted-foreground">
              <li>Upload the original photo of each person or group</li>
              <li>Choose an art style in the next step</li>
              <li>Use an AI tool (Grok, Midjourney) to generate a styled version</li>
              <li>Upload the styled version using the &quot;Upload styled&quot; button on each card</li>
              <li>Compose all styled figures together on the canvas</li>
            </ol>
          </div>
        </CardContent>
      </Card>

      {isLoading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => <Skeleton key={i} className="h-36 rounded-xl" />)}
        </div>
      ) : figures?.length ? (
        <div className="space-y-4">
          {figures.map(figure => (
            <FigureCard key={figure.id} figure={figure} projectId={id} />
          ))}
        </div>
      ) : (
        <p className="text-base text-muted-foreground text-center py-6">
          No figures yet. Drop photos above to get started.
        </p>
      )}

      {figures && figures.length > 0 && (
        <div className="flex justify-end pt-2">
          <Link href={`/project/${id}/style`}>
            <Button>
              Continue to Style <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </Link>
        </div>
      )}
    </div>
  )
}
