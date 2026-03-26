'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { Figure } from '@/types/database'
import type { CreateFigure, UpdateFigure } from '@/lib/schemas/validation'

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init)
  const json = await res.json()
  if (!json.success) throw new Error(json.error || 'Request failed')
  return json.data
}

export function useFigures(projectId: string) {
  return useQuery<Figure[]>({
    queryKey: ['figures', projectId],
    queryFn: () => fetchJson(`/api/figures?project_id=${projectId}`),
    enabled: !!projectId,
  })
}

export function useCreateFigure() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: CreateFigure) =>
      fetchJson<Figure>('/api/figures', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['figures', variables.project_id] })
    },
  })
}

export function useUpdateFigure(projectId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateFigure }) =>
      fetchJson<Figure>(`/api/figures/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['figures', projectId] })
    },
  })
}

export function useDeleteFigure(projectId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) =>
      fetchJson(`/api/figures/${id}`, { method: 'DELETE' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['figures', projectId] })
    },
  })
}
