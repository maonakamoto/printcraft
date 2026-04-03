import { cmToPixels, getTotalDimensions, getPanelBounds } from './surface'
import type { Panel } from '@/types/database'

export interface ExportDimensions {
  total_width_px: number
  total_height_px: number
  panels: { index: number; x_px: number; y_px: number; width_px: number; height_px: number }[]
}

export function calculateExportDimensions(
  panels: Panel[],
  dpi: number,
  bleedMm: number
): ExportDimensions {
  const bleedCm = bleedMm / 10
  const bounds = getPanelBounds(panels)
  const { width_cm, height_cm } = getTotalDimensions(panels)

  const total_width_px = cmToPixels(width_cm + bleedCm * 2, dpi)
  const total_height_px = cmToPixels(height_cm + bleedCm * 2, dpi)

  const panelExports = bounds.map((b, i) => ({
    index: i,
    x_px: cmToPixels(b.x_cm, dpi),
    y_px: 0,
    width_px: cmToPixels(b.width_cm + bleedCm * 2, dpi),
    height_px: cmToPixels(b.height_cm + bleedCm * 2, dpi),
  }))

  return { total_width_px, total_height_px, panels: panelExports }
}

export function getPixelRatio(
  canvasWidth: number,
  targetWidthPx: number
): number {
  return targetWidthPx / canvasWidth
}
