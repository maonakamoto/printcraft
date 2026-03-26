'use client'

import { use, useState } from 'react'
import { useSurface } from '@/hooks/useSurface'
import { useFigures } from '@/hooks/useFigures'
import { calculateExportDimensions } from '@/lib/domain/export'
import { getTotalDimensions } from '@/lib/domain/surface'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Download } from 'lucide-react'

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
      <div className="p-6 max-w-3xl mx-auto text-center py-20">
        <h2 className="text-lg font-medium mb-1">No surface defined</h2>
        <p className="text-sm text-muted-foreground">Define your surface before exporting.</p>
      </div>
    )
  }

  const exportDims = calculateExportDimensions(surface.panels, dpi, surface.bleed_mm)
  const { width_cm, height_cm } = getTotalDimensions(surface.panels)
  const styledCount = figures?.filter(f => f.styled_url).length ?? 0
  const totalCount = figures?.length ?? 0

  return (
    <div className="p-6 max-w-3xl mx-auto w-full space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight">Export</h2>
        <p className="text-sm text-muted-foreground">
          Generate print-ready files for your artwork
        </p>
      </div>

      {/* Summary */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Project Summary</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Surface</span>
            <span>{width_cm.toFixed(1)} x {height_cm.toFixed(1)} cm ({surface.panels.length} panel{surface.panels.length > 1 ? 's' : ''})</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Figures</span>
            <span>{styledCount} styled / {totalCount} total</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Dead zones</span>
            <span>{surface.dead_zones.length}</span>
          </div>
        </CardContent>
      </Card>

      <Separator />

      {/* DPI Selection */}
      <div className="space-y-3">
        <Label>Resolution</Label>
        <div className="grid grid-cols-3 gap-3">
          {DPI_OPTIONS.map(opt => (
            <Card
              key={opt.value}
              className={`cursor-pointer transition-all ${dpi === opt.value ? 'border-primary ring-1 ring-primary' : 'hover:border-primary/50'}`}
              onClick={() => setDpi(opt.value)}
            >
              <CardContent className="p-3 text-center">
                <p className="font-medium text-sm">{opt.label}</p>
                <p className="text-xs text-muted-foreground">{opt.desc}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <Separator />

      {/* Export dimensions */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Output Dimensions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Total image</span>
            <span>{exportDims.total_width_px} x {exportDims.total_height_px} px</span>
          </div>
          {exportDims.panels.map(panel => (
            <div key={panel.index} className="flex justify-between text-sm">
              <span className="text-muted-foreground">Panel {panel.index + 1}</span>
              <span>{panel.width_px} x {panel.height_px} px</span>
            </div>
          ))}
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Bleed</span>
            <span>{surface.bleed_mm} mm</span>
          </div>
        </CardContent>
      </Card>

      {styledCount < totalCount && (
        <div className="text-sm text-amber-500">
          {totalCount - styledCount} figure(s) don&apos;t have styled versions yet. They will use the original photo.
        </div>
      )}

      <a href={`/project/${id}/compose`}>
        <Button className="w-full" size="lg">
          <Download className="h-4 w-4 mr-2" />
          Go to Compose to Export PNG
        </Button>
      </a>

      <p className="text-xs text-muted-foreground text-center">
        Use the &quot;Export PNG&quot; button in the Compose toolbar to download your composition.
        Per-panel splitting at exact DPI will be available in Phase 2.
      </p>
    </div>
  )
}
