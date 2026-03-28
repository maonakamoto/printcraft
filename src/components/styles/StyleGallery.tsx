'use client'

import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import { Check } from 'lucide-react'
import type { Style } from '@/types/database'

interface StyleGalleryProps {
  styles: Style[]
  selectedId: string | null
  onSelect: (id: string) => void
}

export function StyleGallery({ styles, selectedId, onSelect }: StyleGalleryProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {styles.map(style => {
        const isSelected = style.id === selectedId
        return (
          <Card
            key={style.id}
            role="button"
            tabIndex={0}
            className={cn(
              'cursor-pointer transition-all duration-200 hover:-translate-y-0.5',
              isSelected
                ? 'ring-2 ring-primary shadow-lg shadow-primary/10'
                : 'hover:ring-1 hover:ring-primary/30'
            )}
            onClick={() => onSelect(style.id)}
            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelect(style.id) } }}
          >
            <CardContent className="p-5">
              <div className="flex items-start justify-between mb-3">
                <h3 className="font-semibold text-base">{style.name}</h3>
                {isSelected && (
                  <div className="h-6 w-6 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                    <Check className="h-3.5 w-3.5 text-primary-foreground" />
                  </div>
                )}
              </div>
              <p className="text-sm text-primary/80 font-medium italic mb-2">{style.emotional_tone}</p>
              <p className="text-sm text-muted-foreground line-clamp-3">{style.description}</p>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
