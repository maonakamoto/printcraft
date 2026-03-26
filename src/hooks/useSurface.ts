'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { Surface } from '@/types/database'
import type { UpsertSurface } from '@/lib/schemas/validation'

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init)
  const json = await res.json()
  if (!json.success) throw new Error(json.error || 'Request failed')
  return json.data
}

export function useSurface(projectId: string) {
  return useQuery<Surface | null>({
    queryKey: ['surface', projectId],
    queryFn: async () => {
      const res = await fetch(`/api/surfaces?project_id=${projectId}`)
      const json = await res.json()
      return json.data ?? null
    },
    enabled: !!projectId,
  })
}

export function useUpsertSurface(projectId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: UpsertSurface) =>
      fetchJson<Surface>('/api/surfaces', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['surface', projectId] })
    },
  })
}
