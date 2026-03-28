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
    <div className="p-8 max-w-5xl mx-auto w-full space-y-8">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Art Style</h2>
        <p className="text-base text-muted-foreground mt-1">
          Choose the emotional tone for your artwork
        </p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => <Skeleton key={i} className="h-40 rounded-xl" />)}
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
              Continue to Surface <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </Link>
        </div>
      )}
    </div>
  )
}
