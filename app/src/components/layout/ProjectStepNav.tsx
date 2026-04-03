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

  const activeIndex = STEPS.findIndex(s => pathname.endsWith(`/${s.href}`))

  return (
    <nav className="border-b border-white/[0.06] bg-background/80 backdrop-blur-xl">
      <div className="flex items-center gap-2 sm:gap-3 px-4 sm:px-6 md:px-8 py-3 max-w-7xl mx-auto">
        {/* Back button */}
        <Link
          href="/projects"
          className="flex items-center gap-1.5 px-2 sm:px-3 py-2 text-sm text-muted-foreground hover:text-foreground rounded-lg hover:bg-white/[0.04] transition-all shrink-0"
        >
          <ArrowLeft className="h-4 w-4" />
          <span className="hidden sm:inline max-w-32 truncate">{project?.name ?? 'Back'}</span>
        </Link>

        <div className="h-5 w-px bg-white/[0.08] shrink-0" />

        {/* Steps — horizontally scrollable on mobile */}
        <div className="flex items-center gap-0.5 overflow-x-auto scrollbar-none -mx-1 px-1">
          {STEPS.map((step, i) => {
            const href = `/project/${projectId}/${step.href}`
            const isActive = pathname.endsWith(`/${step.href}`)
            const isComplete = completedSteps.has(step.id)
            const isPast = i < activeIndex

            return (
              <div key={step.id} className="flex items-center shrink-0">
                {/* Connector line — hidden on mobile */}
                {i > 0 && (
                  <div
                    className={cn(
                      'step-connector mx-1 hidden md:block',
                      (isPast || (isComplete && i < activeIndex)) && 'completed'
                    )}
                  />
                )}

                <Link
                  href={href}
                  className={cn(
                    'relative flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-4 py-2 text-sm font-medium rounded-full transition-all whitespace-nowrap',
                    isActive
                      ? 'bg-primary text-primary-foreground shadow-md shadow-primary/20'
                      : isComplete
                        ? 'text-foreground/80 hover:text-foreground hover:bg-white/[0.04]'
                        : 'text-muted-foreground hover:text-foreground hover:bg-white/[0.04]'
                  )}
                >
                  {isComplete && !isActive ? (
                    <div className="h-5 w-5 rounded-full bg-primary/20 flex items-center justify-center">
                      <Check className="h-3 w-3 text-primary" />
                    </div>
                  ) : (
                    <step.icon className="h-4 w-4" />
                  )}
                  <span className="hidden sm:inline">{step.label}</span>
                </Link>
              </div>
            )
          })}
        </div>
      </div>
    </nav>
  )
}
