'use client'

import Link from 'next/link'
import { useAuth } from '@/components/providers/AuthProvider'
import { AppShell } from '@/components/layout/AppShell'
import { Button } from '@/components/ui/button'
import {
  Users,
  Palette,
  Layers,
  Ruler,
  Download,
  Sparkles,
  ArrowRight,
  Camera,
  Frame,
  Gem,
} from 'lucide-react'

const FEATURES = [
  {
    icon: Camera,
    title: 'Upload Real Photos',
    description: 'Drop in photos of the people you love. Each one becomes a figure in your composition.',
  },
  {
    icon: Palette,
    title: 'Choose an Art Style',
    description: 'Retro travel poster, oil portrait, watercolor, pop art — pick the emotional tone that fits.',
  },
  {
    icon: Frame,
    title: 'Print on Any Surface',
    description: 'Shower glass, canvas, metal, tile. Define your physical surface and we handle the rest.',
  },
]

const STEPS = [
  { number: '01', title: 'Upload', description: 'Add photos of each person', icon: Users },
  { number: '02', title: 'Style', description: 'Pick your art style', icon: Palette },
  { number: '03', title: 'Surface', description: 'Define the physical print', icon: Ruler },
  { number: '04', title: 'Compose', description: 'Arrange the scene', icon: Layers },
  { number: '05', title: 'Export', description: 'Download print-ready files', icon: Download },
]

const SHOWCASES = [
  {
    title: 'Memorial Portraits',
    description: 'Bring together people who were never in the same place — grandparents with grandchildren, friends across decades.',
    tone: 'Sorrow + Love + Longing',
  },
  {
    title: 'Celebration Artwork',
    description: 'A friend group scattered across continents, reunited in a single scene. The gathering that should have happened.',
    tone: 'Joy + Nostalgia',
  },
  {
    title: 'Passion Projects',
    description: 'Enthusiast communities united in their element. Car clubs, musicians, athletes — together in art.',
    tone: 'Pride + Identity',
  },
]

export default function Home() {
  const { user } = useAuth()

  return (
    <AppShell>
      {/* Hero */}
      <section className="relative hero-gradient overflow-hidden">
        <div className="absolute inset-0 bg-dots opacity-40" />
        <div className="relative max-w-5xl mx-auto px-6 pt-32 pb-28 text-center">
          <div className="animate-slide-up">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-white/[0.08] bg-white/[0.03] text-sm text-muted-foreground mb-8">
              <Sparkles className="h-3.5 w-3.5 text-primary" />
              Scene composer for physical art
            </div>
          </div>

          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-extralight tracking-tight leading-[1.05] animate-slide-up-delay-1">
            Bring people together.
            <br />
            <span className="text-gradient font-light">In art.</span>
          </h1>

          <p className="max-w-2xl mx-auto mt-8 text-lg sm:text-xl text-muted-foreground font-light leading-relaxed animate-slide-up-delay-2">
            Turn separate photos of real people into one unified artwork —
            printed on surfaces that matter. Shower glass, canvas, metal, tile.
          </p>

          <div className="flex items-center justify-center gap-4 mt-12 animate-slide-up-delay-3">
            <Link href={user ? '/projects' : '/login'}>
              <Button size="lg" className="h-13 px-8 text-base font-medium rounded-full">
                {user ? 'Go to Projects' : 'Get Started'}
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </Link>
            <a href="#how-it-works">
              <Button variant="ghost" size="lg" className="h-13 px-8 text-base font-medium rounded-full text-muted-foreground hover:text-foreground">
                How it works
              </Button>
            </a>
          </div>
        </div>

        {/* Bottom gradient fade */}
        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-background to-transparent" />
      </section>

      {/* Section divider */}
      <div className="section-divider" />

      {/* What it does — Feature grid */}
      <section className="max-w-5xl mx-auto px-6 py-28">
        <div className="text-center mb-16">
          <p className="text-sm font-medium tracking-widest uppercase text-primary mb-4 animate-fade-in">
            What it does
          </p>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extralight tracking-tight">
            From photos to physical art.
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {FEATURES.map((feature, i) => (
            <div
              key={feature.title}
              className={`group p-8 rounded-2xl border border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.04] transition-all duration-500 card-hover animate-slide-up-delay-${i + 1}`}
            >
              <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center mb-6 group-hover:bg-primary/15 transition-colors">
                <feature.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-lg font-medium mb-3">{feature.title}</h3>
              <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="section-divider" />

      {/* How it works — Step flow */}
      <section id="how-it-works" className="max-w-5xl mx-auto px-6 py-28 scroll-mt-20">
        <div className="text-center mb-16">
          <p className="text-sm font-medium tracking-widest uppercase text-primary mb-4">
            How it works
          </p>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extralight tracking-tight">
            Five steps to your artwork.
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
          {STEPS.map((step, i) => (
            <div key={step.number} className={`relative animate-slide-up-delay-${Math.min(i + 1, 4)}`}>
              <div className="flex flex-col items-center text-center p-6">
                <span className="text-4xl font-extralight text-primary/30 mb-4 tabular-nums">{step.number}</span>
                <div className="h-12 w-12 rounded-full border border-white/[0.08] bg-white/[0.03] flex items-center justify-center mb-4">
                  <step.icon className="h-5 w-5 text-foreground/80" />
                </div>
                <h3 className="font-medium mb-1">{step.title}</h3>
                <p className="text-sm text-muted-foreground">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <div className="section-divider" />

      {/* Showcase section */}
      <section className="max-w-5xl mx-auto px-6 py-28">
        <div className="text-center mb-16">
          <p className="text-sm font-medium tracking-widest uppercase text-primary mb-4">
            Use cases
          </p>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extralight tracking-tight">
            Art that means something.
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {SHOWCASES.map((item, i) => (
            <div
              key={item.title}
              className={`group p-8 rounded-2xl border border-white/[0.06] bg-white/[0.02] transition-all duration-500 card-hover animate-slide-up-delay-${i + 1}`}
            >
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary/8 text-xs font-medium text-primary mb-6">
                <Gem className="h-3 w-3" />
                {item.tone}
              </div>
              <h3 className="text-xl font-medium mb-3">{item.title}</h3>
              <p className="text-muted-foreground leading-relaxed">{item.description}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="section-divider" />

      {/* CTA */}
      <section className="relative hero-gradient overflow-hidden">
        <div className="max-w-3xl mx-auto px-6 py-28 text-center">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extralight tracking-tight mb-6">
            Ready to create?
          </h2>
          <p className="text-lg text-muted-foreground mb-10 max-w-xl mx-auto">
            Upload your photos, choose a style, define your surface. Your artwork is waiting.
          </p>
          <Link href={user ? '/projects' : '/login'}>
            <Button size="lg" className="h-13 px-10 text-base font-medium rounded-full">
              {user ? 'Open Projects' : 'Get Started'}
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/[0.06]">
        <div className="max-w-5xl mx-auto px-6 py-12 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="text-lg font-semibold tracking-tight">PrintCraft</span>
            <span className="text-sm text-muted-foreground">Scene composer for physical art</span>
          </div>
          <p className="text-sm text-muted-foreground">
            Made for people who print their memories.
          </p>
        </div>
      </footer>
    </AppShell>
  )
}
