'use client'

import { useEffect, useRef } from 'react'
import { Container } from '../ui/container'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

// Register ScrollTrigger plugin
if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger)
}

export function Aggregation() {
  const sectionRef = useRef<HTMLElement>(null)
  const cardsRef = useRef<HTMLDivElement>(null)
  const listRef = useRef<HTMLDivElement>(null)
  const statsRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!sectionRef.current || !cardsRef.current || !listRef.current || !statsRef.current) return

    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (prefersReducedMotion) return

    const ctx = gsap.context(() => {
      // Set up the ScrollTrigger
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 20%',
          end: 'bottom 80%',
          scrub: 1,
          markers: false, // Set to true for debugging
        },
      })

      // Animation sequence
      // 1. Cards fly in and stack (0-30%)
      tl.fromTo(
        '.recipe-card',
        {
          opacity: 0,
          y: 100,
          scale: 0.8,
          rotateX: 15,
        },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          rotateX: 0,
          stagger: 0.1,
          duration: 0.3,
          ease: 'power3.out',
        }
      )

      // 2. Cards compress and merge toward center (30-50%)
      tl.to('.recipe-card', {
        scale: 0.9,
        y: -20,
        stagger: 0.05,
        duration: 0.2,
        ease: 'power2.in',
      })

      // 3. Stats counter animation (40-60%)
      tl.fromTo(
        statsRef.current,
        {
          opacity: 0,
          y: 30,
        },
        {
          opacity: 1,
          y: 0,
          duration: 0.2,
        },
        '<0.1'
      )

      // 4. Grocery list items cascade in (60-100%)
      tl.fromTo(
        '.grocery-item',
        {
          opacity: 0,
          x: -30,
          scale: 0.95,
        },
        {
          opacity: 1,
          x: 0,
          scale: 1,
          stagger: 0.08,
          duration: 0.3,
          ease: 'power3.out',
        },
        '<0.1'
      )

      // Parallax effect on cards vs list
      gsap.to(cardsRef.current, {
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top bottom',
          end: 'bottom top',
          scrub: true,
        },
        y: -50,
        ease: 'none',
      })

      gsap.to(listRef.current, {
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top bottom',
          end: 'bottom top',
          scrub: true,
        },
        y: 50,
        ease: 'none',
      })
    }, sectionRef)

    return () => ctx.revert()
  }, [])

  return (
    <section
      id="aggregation"
      ref={sectionRef}
      className="py-20 md:py-32 lg:py-40 bg-gradient-to-b from-accent-50 to-white overflow-hidden"
    >
      <Container>
        {/* Section Label */}
        <div className="text-center mb-8">
          <span className="label inline-block px-6 py-2 bg-accent-100 text-accent-700 rounded-full text-sm font-semibold uppercase tracking-wider">
            AGGREGATE
          </span>
        </div>

        {/* Headline */}
        <div className="text-center mb-16">
          <h2 className="heading-section text-4xl md:text-5xl lg:text-6xl mb-6 text-secondary-800 font-black">
            One list. Zero duplicates.
          </h2>
          <p className="body-large text-xl md:text-2xl text-neutral-600 max-w-2xl mx-auto">
            We combine ingredients across all your planned meals. Like magic, but it's math.
          </p>
        </div>

        {/* Stats */}
        <div ref={statsRef} className="text-center mb-20 opacity-0">
          <p className="text-5xl md:text-6xl font-black text-accent-600 mb-4 tracking-tight">
            3 recipes × 4 servings
          </p>
          <p className="text-2xl md:text-3xl font-light text-neutral-600">
            = 12 servings optimized
          </p>
          <p className="text-xl text-accent-700 font-semibold mt-2">
            Consolidated 47 items → 23 unique ingredients
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Before: Recipe Cards */}
          <div ref={cardsRef} className="space-y-6">
            <div className="recipe-card bg-white rounded-3xl p-6 shadow-xl border border-accent-200 opacity-0">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-accent-400 rounded-2xl flex items-center justify-center text-white font-bold text-sm">
                  2x
                </div>
                <div>
                  <h4 className="font-semibold text-lg text-secondary-800">Garlic</h4>
                  <p className="text-sm text-neutral-500">From Ratatouille + Risotto</p>
                </div>
              </div>
            </div>
            <div className="recipe-card bg-white rounded-3xl p-6 shadow-xl border border-accent-200 opacity-0">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-accent-400 rounded-2xl flex items-center justify-center text-white font-bold text-sm">
                  3x
                </div>
                <div>
                  <h4 className="font-semibold text-lg text-secondary-800">Olive Oil</h4>
                  <p className="text-sm text-neutral-500">From 3 recipes</p>
                </div>
              </div>
            </div>
          </div>

          {/* After: Consolidated List */}
          <div ref={listRef}>
            <h3 className="text-2xl font-bold text-secondary-800 mb-8 text-center lg:text-left">
              Your Smart Grocery List
            </h3>
            <div className="space-y-3">
              {/* Produce */}
              <div className="grocery-item bg-white rounded-xl shadow-md p-4 border-l-4 border-accent-500 hover:shadow-lg transition-all opacity-0">
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded-full bg-accent-400 flex items-center justify-center text-xs font-bold text-white">✓</div>
                  <span className="font-medium text-secondary-800 flex-1">Garlic</span>
                  <span className="bg-accent-100 text-accent-700 px-3 py-1 rounded-full text-sm font-mono">5 cloves</span>
                </div>
              </div>

              <div className="grocery-item bg-white rounded-xl shadow-md p-4 border-l-4 border-accent-500 hover:shadow-lg transition-all opacity-0">
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded-full bg-accent-400 flex items-center justify-center text-xs font-bold text-white">✓</div>
                  <span className="font-medium text-secondary-800 flex-1">Cherry Tomatoes</span>
                  <span className="bg-accent-100 text-accent-700 px-3 py-1 rounded-full text-sm font-mono">2 lbs</span>
                </div>
              </div>

              {/* Dairy */}
              <div className="grocery-item bg-white rounded-xl shadow-md p-4 border-l-4 border-primary-400 hover:shadow-lg transition-all opacity-0">
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded-full bg-primary-400 flex items-center justify-center text-xs font-bold text-white">✓</div>
                  <span className="font-medium text-secondary-800 flex-1">Parmesan Cheese</span>
                  <span className="bg-primary-100 text-primary-700 px-3 py-1 rounded-full text-sm font-mono">4 oz</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Container>
    </section>
  )
}
