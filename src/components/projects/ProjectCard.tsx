'use client'

import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Trash2, Image as ImageIcon } from 'lucide-react'
import type { Project } from '@/types/database'

const STATUS_LABELS: Record<string, string> = {
  draft: 'Draft',
  uploading: 'Uploading',
  generating: 'Generating',
  composing: 'Composing',
  previewing: 'Previewing',
  exported: 'Exported',
  printed: 'Printed',
}

interface ProjectCardProps {
  project: Project
  onDelete: (id: string) => void
}

export function ProjectCard({ project, onDelete }: ProjectCardProps) {
  return (
    <Card className="group relative transition-all duration-200 hover:ring-1 hover:ring-primary/30 hover:shadow-lg hover:shadow-primary/5 hover:-translate-y-0.5">
      <Link href={`/project/${project.id}/figures`} className="block">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <CardTitle className="text-lg">{project.name}</CardTitle>
            <Badge variant="secondary" className="text-xs">
              {STATUS_LABELS[project.status] ?? project.status}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          {project.description && (
            <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
              {project.description}
            </p>
          )}
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            {project.style && (
              <span className="flex items-center gap-1.5">
                <ImageIcon className="h-4 w-4" />
                {project.style.name}
              </span>
            )}
          </div>
        </CardContent>
      </Link>
      <Button
        variant="ghost"
        size="icon"
        className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8"
        onClick={(e) => { e.preventDefault(); onDelete(project.id) }}
      >
        <Trash2 className="h-4 w-4 text-destructive" />
      </Button>
    </Card>
  )
}
