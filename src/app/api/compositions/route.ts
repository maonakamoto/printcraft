import { NextResponse, type NextRequest } from 'next/server'
import { getApiClient } from '@/lib/supabase/api-client'
import { upsertCompositionSchema } from '@/lib/schemas/validation'

export async function GET(request: NextRequest) {
  const { supabase } = await getApiClient()

  const projectId = request.nextUrl.searchParams.get('project_id')
  if (!projectId) return NextResponse.json({ success: false, error: 'project_id required' }, { status: 400 })

  const { data, error } = await supabase
    .from('compositions')
    .select('*')
    .eq('project_id', projectId)
    .order('version', { ascending: false })
    .limit(1)
    .single()

  if (error) return NextResponse.json({ success: false, data: null })
  return NextResponse.json({ success: true, data })
}

export async function POST(request: NextRequest) {
  const { supabase } = await getApiClient()

  const body = await request.json()
  const parsed = upsertCompositionSchema.safeParse(body)
  if (!parsed.success) {
    return NextResponse.json({ success: false, error: 'Invalid data', details: parsed.error.flatten() }, { status: 400 })
  }

  const { data: existing } = await supabase
    .from('compositions')
    .select('version')
    .eq('project_id', parsed.data.project_id)
    .order('version', { ascending: false })
    .limit(1)
    .single()

  const nextVersion = (existing?.version ?? 0) + 1

  const { data, error } = await supabase
    .from('compositions')
    .insert({ ...parsed.data, version: nextVersion })
    .select()
    .single()

  if (error) return NextResponse.json({ success: false, error: error.message }, { status: 500 })
  return NextResponse.json({ success: true, data }, { status: 201 })
}
