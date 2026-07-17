import type { Panel, SeamPosition, DeadZone } from '@/types/database'

export function cmToPixels(cm: number, dpi: number): number {
  return Math.round((cm / 2.54) * dpi)
}

export function pixelsToCm(px: number, dpi: number): number {
  return (px * 2.54) / dpi
}

export function getTotalDimensions(panels: Panel[]): { width_cm: number; height_cm: number } {
  const width_cm = panels.reduce((sum, p) => sum + p.width_cm, 0)
  const height_cm = Math.max(...panels.map(p => p.height_cm))
  return { width_cm, height_cm }
}

export function getSeamPositionsFromPanels(panels: Panel[]): SeamPosition[] {
  const seams: SeamPosition[] = []
  let x = 0
  for (let i = 0; i < panels.length - 1; i++) {
    x += panels[i].width_cm
    seams.push({ x_cm: x })
  }
  return seams
}

export function isInDeadZone(
  x_cm: number,
  y_cm: number,
  width_cm: number,
  height_cm: number,
  deadZones: DeadZone[]
): DeadZone | null {
  for (const zone of deadZones) {
    const overlap =
      x_cm < zone.x_cm + zone.width_cm &&
      x_cm + width_cm > zone.x_cm &&
      y_cm < zone.y_cm + zone.height_cm &&
      y_cm + height_cm > zone.y_cm

    if (overlap) return zone
  }
  return null
}

export function isNearSeam(
  x_cm: number,
  width_cm: number,
  seams: SeamPosition[],
  bufferCm: number = 10
): boolean {
  for (const seam of seams) {
    const left = x_cm
    const right = x_cm + width_cm
    if (left < seam.x_cm + bufferCm && right > seam.x_cm - bufferCm) {
      return true
    }
  }
  return false
}

export function getPanelBounds(panels: Panel[]): { x_cm: number; width_cm: number; height_cm: number }[] {
  const bounds: { x_cm: number; width_cm: number; height_cm: number }[] = []
  let x = 0
  for (const panel of panels) {
    bounds.push({ x_cm: x, width_cm: panel.width_cm, height_cm: panel.height_cm })
    x += panel.width_cm
  }
  return bounds
}
