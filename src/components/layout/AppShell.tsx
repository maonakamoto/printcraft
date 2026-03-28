'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { useAuth } from '@/components/providers/AuthProvider'
import { Button } from '@/components/ui/button'
import { LogOut } from 'lucide-react'
import type { ReactNode } from 'react'

export function AppShell({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  const router = useRouter()
  const supabase = createClient()

  async function handleLogout() {
    await supabase.auth.signOut()
    router.push('/login')
    router.refresh()
  }

  return (
    <div className="flex flex-col min-h-full">
      <header className="sticky top-0 z-50 glass border-b border-white/[0.06]">
        <div className="flex h-16 items-center justify-between px-8">
          <Link href="/projects" className="text-xl font-bold tracking-tight">
            PrintCraft
          </Link>
          {user && (
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Sign out
            </Button>
          )}
        </div>
      </header>
      <main className="flex-1 flex flex-col animate-in-page">
        {children}
      </main>
    </div>
  )
}
