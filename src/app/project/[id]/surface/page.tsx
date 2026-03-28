'use client'

import { use, useState, useEffect } from 'react'
import { useSurface, useUpsertSurface } from '@/hooks/useSurface'
import { SURFACE_PRESETS, type SurfacePreset } from '@/lib/config/surface-presets'
import { getTotalDimensions, getSeamPositionsFromPanels } from '@/lib/domain/surface'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils'
import { Check, Plus, X, ArrowRight } from 'lucide-react'
import { toast } from 'sonner'
import type { Panel, DeadZone, SurfaceType } from '@/types/database'

export default function SurfacePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const { data: existingSurface } = useSurface(id)
  const upsertSurface = useUpsertSurface(id)

  const [selectedPreset, setSelectedPreset] = useState<string>('custom')
  const [surfaceType, setSurfaceType] = useState<SurfaceType>('custom')
  const [panels, setPanels] = useState<Panel[]>([{ width_cm: 100, height_cm: 100 }])
  const [deadZones, setDeadZones] = useState<DeadZone[]>([])
  const [dpiTarget, setDpiTarget] = useState(200)
  const [bleedMm, setBleedMm] = useState(3)

  useEffect(() => {
    if (existingSurface) {
      setPanels(existingSurface.panels)
      setDeadZones(existingSurface.dead_zones)
      setDpiTarget(existingSurface.dpi_target)
      setBleedMm(existingSurface.bleed_mm)
      setSurfaceType(existingSurface.type)
    }
  }, [existingSurface])

  function applyPreset(preset: SurfacePreset) {
    setSelectedPreset(preset.id)
    setSurfaceType(preset.type)
    setPanels([...preset.panels])
    setDeadZones([...preset.dead_zones])
    setDpiTarget(preset.dpi_target)
    setBleedMm(preset.bleed_mm)
  }

  function updatePanel(index: number, field: keyof Panel, value: number) {
    const updated = [...panels]
    updated[index] = { ...updated[index], [field]: value }
    setPanels(updated)
  }

  function addPanel() {
    setPanels([...panels, { width_cm: 100, height_cm: panels[0]?.height_cm ?? 100 }])
  }

  function removePanel(index: number) {
    if (panels.length <= 1) return
    setPanels(panels.filter((_, i) => i !== index))
  }

  function addDeadZone() {
    setDeadZones([...deadZones, { x_cm: 0, y_cm: 0, width_cm: 40, height_cm: 40, reason: '' }])
  }

  function updateDeadZone(index: number, field: keyof DeadZone, value: string | number) {
    const updated = [...deadZones]
    updated[index] = { ...updated[index], [field]: value }
    setDeadZones(updated)
  }

  function removeDeadZone(index: number) {
    setDeadZones(deadZones.filter((_, i) => i !== index))
  }

  function handleSave() {
    const seams = getSeamPositionsFromPanels(panels)
    upsertSurface.mutate(
      {
        project_id: id,
        type: surfaceType,
        panels,
        seam_positions: seams,
        dead_zones: deadZones,
        dpi_target: dpiTarget,
        bleed_mm: bleedMm,
      },
      {
        onSuccess: () => toast.success('Surface saved'),
        onError: (err) => toast.error(err.message),
      }
    )
  }

  const { width_cm, height_cm } = getTotalDimensions(panels)
  const scale = Math.min(500 / width_cm, 300 / height_cm, 2)

  return (
    <div className="p-8 max-w-5xl mx-auto w-full space-y-8">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Surface</h2>
        <p className="text-base text-muted-foreground mt-1">
          Define the physical surface this artwork will be printed on
        </p>
      </div>

      {/* Presets */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {SURFACE_PRESETS.map(preset => (
          <Card
            key={preset.id}
            className={cn(
              'cursor-pointer transition-all hover:border-primary/50',
              selectedPreset === preset.id && 'border-primary ring-1 ring-primary'
            )}
            onClick={() => applyPreset(preset)}
          >
            <CardContent className="p-3">
              <p className="text-sm font-medium">{preset.name}</p>
              <p className="text-xs text-muted-foreground">{preset.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Separator />

      {/* Panels */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-medium">Panels</h3>
          <Button variant="outline" size="sm" onClick={addPanel}>
            <Plus className="h-3 w-3 mr-1" /> Add Panel
          </Button>
        </div>
        {panels.map((panel, i) => (
          <div key={i} className="flex items-end gap-3">
            <div className="space-y-1">
              <Label className="text-xs">Width (cm)</Label>
              <Input
                type="number"
                value={panel.width_cm}
                onChange={e => updatePanel(i, 'width_cm', parseFloat(e.target.value) || 0)}
                className="w-28 h-8"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Height (cm)</Label>
              <Input
                type="number"
                value={panel.height_cm}
                onChange={e => updatePanel(i, 'height_cm', parseFloat(e.target.value) || 0)}
                className="w-28 h-8"
              />
            </div>
            <Badge variant="outline" className="mb-1">Panel {i + 1}</Badge>
            {panels.length > 1 && (
              <Button variant="ghost" size="icon" className="h-8 w-8 mb-0.5" onClick={() => removePanel(i)}>
                <X className="h-3 w-3" />
              </Button>
            )}
          </div>
        ))}
        <p className="text-xs text-muted-foreground">
          Total: {width_cm.toFixed(1)} x {height_cm.toFixed(1)} cm
        </p>
      </div>

      <Separator />

      {/* Dead Zones */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-medium">Dead Zones</h3>
            <p className="text-xs text-muted-foreground">Areas blocked by fixtures (shower head, faucet, etc.)</p>
          </div>
          <Button variant="outline" size="sm" onClick={addDeadZone}>
            <Plus className="h-3 w-3 mr-1" /> Add Zone
          </Button>
        </div>
        {deadZones.map((zone, i) => (
          <div key={i} className="flex items-end gap-2 flex-wrap">
            <div className="space-y-1">
              <Label className="text-xs">X (cm)</Label>
              <Input type="number" value={zone.x_cm} onChange={e => updateDeadZone(i, 'x_cm', parseFloat(e.target.value) || 0)} className="w-20 h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Y (cm)</Label>
              <Input type="number" value={zone.y_cm} onChange={e => updateDeadZone(i, 'y_cm', parseFloat(e.target.value) || 0)} className="w-20 h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Width</Label>
              <Input type="number" value={zone.width_cm} onChange={e => updateDeadZone(i, 'width_cm', parseFloat(e.target.value) || 0)} className="w-20 h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Height</Label>
              <Input type="number" value={zone.height_cm} onChange={e => updateDeadZone(i, 'height_cm', parseFloat(e.target.value) || 0)} className="w-20 h-8" />
            </div>
            <div className="space-y-1 flex-1 min-w-[120px]">
              <Label className="text-xs">Reason</Label>
              <Input value={zone.reason} onChange={e => updateDeadZone(i, 'reason', e.target.value)} placeholder="e.g., Shower fixture" className="h-8" />
            </div>
            <Button variant="ghost" size="icon" className="h-8 w-8 mb-0.5" onClick={() => removeDeadZone(i)}>
              <X className="h-3 w-3" />
            </Button>
          </div>
        ))}
      </div>

      <Separator />

      {/* DPI + Bleed */}
      <div className="flex gap-6">
        <div className="space-y-1">
          <Label className="text-xs">DPI Target</Label>
          <Input type="number" value={dpiTarget} onChange={e => setDpiTarget(parseInt(e.target.value) || 200)} className="w-28 h-8" />
        </div>
        <div className="space-y-1">
          <Label className="text-xs">Bleed (mm)</Label>
          <Input type="number" value={bleedMm} onChange={e => setBleedMm(parseFloat(e.target.value) || 0)} className="w-28 h-8" />
        </div>
      </div>

      {/* Visual Preview */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-end gap-0" style={{ height: height_cm * scale }}>
            {panels.map((panel, i) => {
              return (
                <div
                  key={i}
                  className="border border-border relative bg-muted/30"
                  style={{
                    width: panel.width_cm * scale,
                    height: panel.height_cm * scale,
                    borderRight: i < panels.length - 1 ? '2px dashed hsl(var(--destructive))' : undefined,
                  }}
                >
                  <span className="absolute top-1 left-1 text-[10px] text-muted-foreground">
                    P{i + 1}: {panel.width_cm}x{panel.height_cm}
                  </span>
                  {/* Dead zones within this panel */}
                  {deadZones.map((zone, zi) => {
                    const panelX = panels.slice(0, i).reduce((s, p) => s + p.width_cm, 0)
                    const zoneRelX = zone.x_cm - panelX
                    if (zoneRelX < 0 || zoneRelX >= panel.width_cm) return null
                    return (
                      <div
                        key={zi}
                        className="absolute bg-destructive/20 border border-destructive/50"
                        style={{
                          left: zoneRelX * scale,
                          bottom: zone.y_cm * scale,
                          width: zone.width_cm * scale,
                          height: zone.height_cm * scale,
                        }}
                      >
                        <span className="text-[8px] text-destructive p-0.5">{zone.reason}</span>
                      </div>
                    )
                  })}
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-3 justify-between">
        <Button onClick={handleSave} disabled={upsertSurface.isPending}>
          {upsertSurface.isPending ? 'Saving...' : existingSurface ? 'Update Surface' : 'Save Surface'}
        </Button>
        {existingSurface && (
          <Link href={`/project/${id}/compose`}>
            <Button variant="outline">
              Continue to Compose <ArrowRight className="h-4 w-4 ml-1" />
            </Button>
          </Link>
        )}
      </div>
    </div>
  )
}
