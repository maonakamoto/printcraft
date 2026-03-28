'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter, usePathname } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { useAuth } from '@/components/providers/AuthProvider'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { LogOut, Menu, X, User } from 'lucide-react'
import type { ReactNode } from 'react'

const NAV_LINKS = [
  { href: '/projects', label: 'Projects' },
  { href: '/#how-it-works', label: 'How It Works' },
]

export function AppShell({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  const router = useRouter()
  const pathname = usePathname()
  const supabase = createClient()
  const [scrolled, setScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    function onScroll() {
      setScrolled(window.scrollY > 10)
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false)
  }, [pathname])

  async function handleLogout() {
    await supabase.auth.signOut()
    router.push('/login')
    router.refresh()
  }

  return (
    <div className="flex flex-col min-h-full">
      <header
        className={cn(
          'sticky top-0 z-50 transition-all duration-300',
          scrolled
            ? 'glass-strong border-b border-white/[0.06] shadow-lg shadow-black/10'
            : 'bg-transparent'
        )}
      >
        <div className="flex h-14 items-center justify-between px-6 sm:px-8 max-w-7xl mx-auto w-full">
          {/* Logo */}
          <Link
            href="/"
            className="text-lg font-semibold tracking-tight text-foreground hover:text-primary transition-colors"
          >
            PrintCraft
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-1">
            {NAV_LINKS.map(link => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  'px-4 py-2 text-sm font-medium rounded-full transition-colors',
                  pathname === link.href
                    ? 'text-foreground'
                    : 'text-muted-foreground hover:text-foreground'
                )}
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Right side */}
          <div className="flex items-center gap-2">
            {user ? (
              <div className="hidden md:flex items-center gap-2">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.04]">
                  <div className="h-6 w-6 rounded-full bg-primary/20 flex items-center justify-center">
                    <User className="h-3.5 w-3.5 text-primary" />
                  </div>
                  <span className="text-sm text-muted-foreground max-w-32 truncate">
                    {user.email?.split('@')[0]}
                  </span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-muted-foreground hover:text-foreground rounded-full h-8 w-8 p-0"
                  onClick={handleLogout}
                >
                  <LogOut className="h-4 w-4" />
                </Button>
              </div>
            ) : (
              <Link href="/login" className="hidden md:block">
                <Button variant="ghost" size="sm" className="text-sm rounded-full">
                  Sign in
                </Button>
              </Link>
            )}

            {/* Mobile menu toggle */}
            <Button
              variant="ghost"
              size="sm"
              className="md:hidden h-8 w-8 p-0"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </Button>
          </div>
        </div>

        {/* Glow line */}
        <div className={cn('h-px glow-line transition-opacity duration-300', scrolled ? 'opacity-100' : 'opacity-0')} />

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden glass-strong border-t border-white/[0.06] animate-fade-in">
            <div className="px-6 py-4 space-y-2">
              {NAV_LINKS.map(link => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="block px-4 py-3 text-sm font-medium text-muted-foreground hover:text-foreground rounded-lg hover:bg-white/[0.04] transition-colors"
                >
                  {link.label}
                </Link>
              ))}
              {user ? (
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-3 text-sm font-medium text-muted-foreground hover:text-foreground rounded-lg hover:bg-white/[0.04] transition-colors"
                >
                  Sign out
                </button>
              ) : (
                <Link
                  href="/login"
                  className="block px-4 py-3 text-sm font-medium text-primary hover:text-foreground rounded-lg hover:bg-white/[0.04] transition-colors"
                >
                  Sign in
                </Link>
              )}
            </div>
          </div>
        )}
      </header>

      <main className="flex-1 flex flex-col">
        {children}
      </main>
    </div>
  )
}
