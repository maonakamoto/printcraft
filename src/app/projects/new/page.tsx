'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useCreateProject } from '@/hooks/useProjects'
import { AppShell } from '@/components/layout/AppShell'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { toast } from 'sonner'

export default function NewProjectPage() {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [sceneDescription, setSceneDescription] = useState('')
  const router = useRouter()
  const createProject = useCreateProject()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    createProject.mutate(
      {
        name,
        description: description || undefined,
        scene_description: sceneDescription || undefined,
      },
      {
        onSuccess: (project) => {
          toast.success('Project created')
          router.push(`/project/${project.id}/figures`)
        },
        onError: (err) => toast.error(err.message),
      }
    )
  }

  return (
    <AppShell>
      <div className="p-6 max-w-lg mx-auto w-full">
        <Card>
          <CardHeader>
            <CardTitle>New Project</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  placeholder="e.g., Amphicar Lake Garda"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description (optional)</Label>
                <Textarea
                  id="description"
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                  placeholder="What is this artwork for?"
                  rows={2}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="scene">Scene Description (optional)</Label>
                <Textarea
                  id="scene"
                  value={sceneDescription}
                  onChange={e => setSceneDescription(e.target.value)}
                  placeholder="e.g., Lake Garda at golden hour, green hills, Italian villages"
                  rows={3}
                />
              </div>
              <div className="flex gap-2 justify-end">
                <Button type="button" variant="ghost" onClick={() => router.back()}>
                  Cancel
                </Button>
                <Button type="submit" disabled={createProject.isPending}>
                  {createProject.isPending ? 'Creating...' : 'Create Project'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
