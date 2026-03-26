'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Users, Palette, Ruler, Layers, Download, Check, ArrowLeft } from 'lucide-react'
import { useProject } from '@/hooks/useProject'
import { useFigures } from '@/hooks/useFigures'
import { useSurface } from '@/hooks/useSurface'

const STEPS = [
  { id: 'figures', label: 'Figures', icon: Users, href: 'figures' },
  { id: 'style', label: 'Style', icon: Palette, href: 'style' },
  { id: 'surface', label: 'Surface', icon: Ruler, href: 'surface' },
  { id: 'compose', label: 'Compose', icon: Layers, href: 'compose' },
  { id: 'export', label: 'Export', icon: Download, href: 'export' },
]

export function ProjectStepNav({ projectId }: { projectId: string }) {
  const pathname = usePathname()
  const { data: project } = useProject(projectId)
  const { data: figures } = useFigures(projectId)
  const { data: surface } = useSurface(projectId)

  const completedSteps = new Set<string>()
  if (figures && figures.length > 0) completedSteps.add('figures')
  if (project?.style_id) completedSteps.add('style')
  if (surface) completedSteps.add('surface')
  if (figures?.some(f => f.styled_url)) completedSteps.add('compose')

  return (
    <nav className="border-b border-border/40">
      <div className="flex items-center gap-1 px-6 overflow-x-auto">
        <Link
          href="/projects"
          className="flex items-center gap-1 px-3 py-3 text-sm text-muted-foreground hover:text-foreground transition-colors mr-2"
        >
          <ArrowLeft className="h-4 w-4" />
          <span className="hidden sm:inline">{project?.name ?? 'Back'}</span>
        </Link>

        <div className="h-6 w-px bg-border/40 mr-2" />

        {STEPS.map((step) => {
          const href = `/project/${projectId}/${step.href}`
          const isActive = pathname.endsWith(`/${step.href}`)
          const isComplete = completedSteps.has(step.id)

          return (
            <Link
              key={step.id}
              href={href}
              className={cn(
                'flex items-center gap-1.5 px-3 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap',
                isActive
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
              )}
            >
              {isComplete && !isActive ? (
                <Check className="h-3.5 w-3.5 text-green-500" />
              ) : (
                <step.icon className="h-3.5 w-3.5" />
              )}
              <span className="hidden sm:inline">{step.label}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
