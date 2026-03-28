'use client'

import Link from 'next/link'
import { useProjects, useDeleteProject } from '@/hooks/useProjects'
import { AppShell } from '@/components/layout/AppShell'
import { ProjectCard } from '@/components/projects/ProjectCard'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Plus, ImageIcon } from 'lucide-react'
import { toast } from 'sonner'

export default function ProjectsPage() {
  const { data: projects, isLoading } = useProjects()
  const deleteProject = useDeleteProject()

  function handleDelete(id: string) {
    if (!confirm('Delete this project?')) return
    deleteProject.mutate(id, {
      onSuccess: () => toast.success('Project deleted'),
      onError: (err) => toast.error(err.message),
    })
  }

  return (
    <AppShell>
      <div className="px-8 py-10 max-w-6xl mx-auto w-full">
        <div className="flex items-center justify-between mb-10">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">Projects</h1>
            <p className="text-base text-muted-foreground mt-1">Your artwork compositions</p>
          </div>
          <Link href="/projects/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Project
            </Button>
          </Link>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-48 rounded-xl" />
            ))}
          </div>
        ) : projects?.length ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map(project => (
              <ProjectCard key={project.id} project={project} onDelete={handleDelete} />
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <ImageIcon className="h-16 w-16 text-muted-foreground/30 mb-6" />
            <h2 className="text-xl font-semibold mb-2">No projects yet</h2>
            <p className="text-base text-muted-foreground mb-6">
              Create your first artwork composition
            </p>
            <Link href="/projects/new">
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                New Project
              </Button>
            </Link>
          </div>
        )}
      </div>
    </AppShell>
  )
}
