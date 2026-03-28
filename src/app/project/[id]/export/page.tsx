'use client'

import { use, useState } from 'react'
import { useSurface } from '@/hooks/useSurface'
import { useFigures } from '@/hooks/useFigures'
import { calculateExportDimensions } from '@/lib/domain/export'
import { getTotalDimensions } from '@/lib/domain/surface'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Download, AlertCircle, ArrowLeft, Check } from 'lucide-react'
import Link from 'next/link'

const DPI_OPTIONS = [
  { value: 150, label: '150 DPI', desc: 'Good for large viewing distance' },
  { value: 200, label: '200 DPI', desc: 'Recommended for most prints' },
  { value: 300, label: '300 DPI', desc: 'Maximum quality, large files' },
]

export default function ExportPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const { data: surface } = useSurface(id)
  const { data: figures } = useFigures(id)
  const [dpi, setDpi] = useState(200)

  if (!surface) {
    return (
      <div className="flex flex-col items-center justify-center py-28 text-center px-6 animate-in-page">
        <div className="h-16 w-16 rounded-2xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-center mb-6">
          <AlertCircle className="h-7 w-7 text-muted-foreground/40" />
        </div>
        <h2 className="text-xl font-light mb-2">No surface defined</h2>
        <p className="text-muted-foreground mb-6">Define your surface before exporting.</p>
        <Link href={`/project/${id}/surface`}>
          <Button variant="outline" className="rounded-full">
            <ArrowLeft className="h-4 w-4 mr-2" /> Go to Surface
          </Button>
        </Link>
      </div>
    )
  }

  const exportDims = calculateExportDimensions(surface.panels, dpi, surface.bleed_mm)
  const { width_cm, height_cm } = getTotalDimensions(surface.panels)
  const styledCount = figures?.filter(f => f.styled_url).length ?? 0
  const totalCount = figures?.length ?? 0

  return (
    <div className="max-w-4xl mx-auto w-full px-6 sm:px-8 py-10 space-y-10 animate-in-page">
      <div>
        <h2 className="text-3xl sm:text-4xl font-extralight tracking-tight">Export</h2>
        <p className="text-muted-foreground mt-2 text-lg font-light">
          Generate print-ready files for your artwork
        </p>
      </div>

      {/* Summary */}
      <div className="rounded-2xl border border-white/[0.06] bg-white/[0.02] overflow-hidden">
        <div className="px-6 py-4 border-b border-white/[0.04]">
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Project Summary</h3>
        </div>
        <div className="p-6 space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Surface</span>
            <span className="font-mono text-sm">{width_cm.toFixed(1)} x {height_cm.toFixed(1)} cm ({surface.panels.length} panel{surface.panels.length > 1 ? 's' : ''})</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Figures</span>
            <span>{styledCount} styled / {totalCount} total</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Dead zones</span>
            <span>{surface.dead_zones.length}</span>
          </div>
        </div>
      </div>

      {/* DPI Selection */}
      <div className="space-y-4">
        <Label className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Resolution</Label>
        <div className="grid grid-cols-3 gap-4">
          {DPI_OPTIONS.map(opt => (
            <button
              key={opt.value}
              className={cn(
                'p-5 rounded-2xl border text-center transition-all duration-300 card-hover',
                dpi === opt.value
                  ? 'border-primary bg-primary/5 ring-1 ring-primary/30 glow-selected'
                  : 'border-white/[0.06] bg-white/[0.02] hover:border-white/[0.12]'
              )}
              onClick={() => setDpi(opt.value)}
            >
              <div className="flex items-center justify-center gap-2 mb-1">
                <p className="font-medium">{opt.label}</p>
                {dpi === opt.value && <Check className="h-4 w-4 text-primary" />}
              </div>
              <p className="text-xs text-muted-foreground">{opt.desc}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Export dimensions */}
      <div className="rounded-2xl border border-white/[0.06] bg-white/[0.02] overflow-hidden">
        <div className="px-6 py-4 border-b border-white/[0.04]">
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Output Dimensions</h3>
        </div>
        <div className="p-6 space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Total image</span>
            <span className="font-mono">{exportDims.total_width_px} x {exportDims.total_height_px} px</span>
          </div>
          {exportDims.panels.map(panel => (
            <div key={panel.index} className="flex justify-between text-sm">
              <span className="text-muted-foreground">Panel {panel.index + 1}</span>
              <span className="font-mono">{panel.width_px} x {panel.height_px} px</span>
            </div>
          ))}
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Bleed</span>
            <span>{surface.bleed_mm} mm</span>
          </div>
        </div>
      </div>

      {styledCount < totalCount && (
        <div className="rounded-2xl border border-primary/20 bg-primary/[0.03] p-5 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-primary mt-0.5 shrink-0" />
          <p className="text-sm text-muted-foreground">
            {totalCount - styledCount} figure(s) don&apos;t have styled versions yet. They will use the original photo.
          </p>
        </div>
      )}

      <a href={`/project/${id}/compose`}>
        <Button className="w-full h-13 text-base font-medium rounded-2xl" size="lg">
          <Download className="h-5 w-5 mr-2" />
          Go to Compose to Export PNG
        </Button>
      </a>

      <p className="text-xs text-muted-foreground text-center leading-relaxed">
        Use the &quot;Export PNG&quot; button in the Compose toolbar to download your composition.
        Per-panel splitting at exact DPI will be available in Phase 2.
      </p>
    </div>
  )
}
