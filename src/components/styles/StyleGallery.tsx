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
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {styles.map(style => {
        const isSelected = style.id === selectedId
        return (
          <Card
            key={style.id}
            className={cn(
              'cursor-pointer transition-all hover:border-primary/50',
              isSelected && 'border-primary ring-1 ring-primary'
            )}
            onClick={() => onSelect(style.id)}
          >
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-medium text-sm">{style.name}</h3>
                {isSelected && (
                  <div className="h-5 w-5 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                    <Check className="h-3 w-3 text-primary-foreground" />
                  </div>
                )}
              </div>
              <p className="text-xs text-primary/80 font-medium mb-1">{style.emotional_tone}</p>
              <p className="text-xs text-muted-foreground line-clamp-3">{style.description}</p>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
