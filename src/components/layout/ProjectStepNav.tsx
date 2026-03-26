'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Users, Palette, Ruler, Layers, Download } from 'lucide-react'

const STEPS = [
  { id: 'figures', label: 'Figures', icon: Users, href: 'figures' },
  { id: 'style', label: 'Style', icon: Palette, href: 'style' },
  { id: 'surface', label: 'Surface', icon: Ruler, href: 'surface' },
  { id: 'compose', label: 'Compose', icon: Layers, href: 'compose' },
  { id: 'export', label: 'Export', icon: Download, href: 'export' },
]

export function ProjectStepNav({ projectId }: { projectId: string }) {
  const pathname = usePathname()

  return (
    <nav className="border-b border-border/40">
      <div className="flex items-center gap-1 px-6 overflow-x-auto">
        {STEPS.map((step) => {
          const href = `/project/${projectId}/${step.href}`
          const isActive = pathname.endsWith(`/${step.href}`)

          return (
            <Link
              key={step.id}
              href={href}
              className={cn(
                'flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap',
                isActive
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
              )}
            >
              <step.icon className="h-4 w-4" />
              {step.label}
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
