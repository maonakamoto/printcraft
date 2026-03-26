'use client'

import { use } from 'react'
import Link from 'next/link'
import { useProject, useUpdateProject } from '@/hooks/useProject'
import { useStyles } from '@/hooks/useStyles'
import { StyleGallery } from '@/components/styles/StyleGallery'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { ArrowRight } from 'lucide-react'
import { toast } from 'sonner'

export default function StylePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const { data: project } = useProject(id)
  const { data: styles, isLoading } = useStyles()
  const updateProject = useUpdateProject(id)

  function handleSelect(styleId: string) {
    updateProject.mutate(
      { style_id: styleId },
      {
        onSuccess: () => toast.success('Style selected'),
        onError: (err) => toast.error(err.message),
      }
    )
  }

  return (
    <div className="p-6 max-w-4xl mx-auto w-full space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight">Art Style</h2>
        <p className="text-sm text-muted-foreground">
          Choose the emotional tone for your artwork
        </p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <Skeleton key={i} className="h-32 rounded-xl" />)}
        </div>
      ) : styles ? (
        <StyleGallery
          styles={styles}
          selectedId={project?.style_id ?? null}
          onSelect={handleSelect}
        />
      ) : null}

      {project?.style_id && (
        <div className="flex justify-end pt-2">
          <Link href={`/project/${id}/surface`}>
            <Button>
              Continue to Surface <ArrowRight className="h-4 w-4 ml-1" />
            </Button>
          </Link>
        </div>
      )}
    </div>
  )
}
