import type { SurfaceType, Panel, SeamPosition, DeadZone } from '@/types/database'

export interface SurfacePreset {
  id: string
  name: string
  description: string
  type: SurfaceType
  panels: Panel[]
  seam_positions: SeamPosition[]
  dead_zones: DeadZone[]
  dpi_target: number
  bleed_mm: number
}

export const SURFACE_PRESETS: SurfacePreset[] = [
  {
    id: 'shower-2-panel',
    name: 'Shower Wall (2 panels)',
    description: 'L-shaped glass shower wall with 2 panels',
    type: 'glass',
    panels: [
      { width_cm: 77.5, height_cm: 190 },
      { width_cm: 119.5, height_cm: 190 },
    ],
    seam_positions: [{ x_cm: 77.5 }],
    dead_zones: [],
    dpi_target: 200,
    bleed_mm: 3,
  },
  {
    id: 'canvas-large',
    name: 'Canvas (100x70)',
    description: 'Large canvas print, landscape',
    type: 'canvas',
    panels: [{ width_cm: 100, height_cm: 70 }],
    seam_positions: [],
    dead_zones: [],
    dpi_target: 200,
    bleed_mm: 5,
  },
  {
    id: 'poster-a1',
    name: 'Poster A1',
    description: '59.4 x 84.1 cm poster',
    type: 'paper',
    panels: [{ width_cm: 84.1, height_cm: 59.4 }],
    seam_positions: [],
    dead_zones: [],
    dpi_target: 300,
    bleed_mm: 3,
  },
  {
    id: 'custom',
    name: 'Custom',
    description: 'Define your own dimensions',
    type: 'custom',
    panels: [{ width_cm: 100, height_cm: 100 }],
    seam_positions: [],
    dead_zones: [],
    dpi_target: 200,
    bleed_mm: 3,
  },
]
