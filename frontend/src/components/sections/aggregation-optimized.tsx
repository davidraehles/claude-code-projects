'use client'

import { useEffect, useRef } from 'react'
import { Container } from '../ui/container'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

/**
 * Optimized Aggregation Section
 * This version uses simplified animations to reduce bundle size impact
 * and improve performance on mobile devices.
 */

// Register ScrollTrigger plugin
if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger)
}

export function AggregationOptimized() {
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
      // Simplified ScrollTrigger with single timeline
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 30%',  // Start earlier for better UX
          end: 'bottom 70%', // End earlier for better performance
          scrub: 1,
          markers: false,
        },
      })

      // Optimized animation sequence (reduced from 4 steps to 2)
      // 1. Cards and list appear together (simplified)
      tl.fromTo(
        ['.recipe-card', '.grocery-item'],
        { opacity: 0, y: 30 },
        {
          opacity: 1,
          y: 0,
          stagger: 0.1,
          duration: 0.2,
          ease: 'power3.out',
        }
      )

      // 2. Stats appear (simplified)
      tl.fromTo(
        statsRef.current,
        { opacity: 0, y: 20 },
        {
          opacity: 1,
          y: 0,
          duration: 0.2,
          ease: 'power3.out',
        },
        '<0.1' // Overlap slightly for smoother transition
      )

      // Single parallax effect (instead of separate ones)
      gsap.to([cardsRef.current, listRef.current], {
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top bottom',
          end: 'bottom top',
          scrub: true,
        },
        y: (i, target) => {
          // Cards move up, list moves down for depth effect
          return target === cardsRef.current ? -30 : 30
        },
        ease: 'none',
      })
    })

    return () => {
      // Clean up ScrollTrigger instances
      ScrollTrigger.getAll().forEach(instance => instance.kill())
      ctx.revert() // Clean up GSAP context
    }
  }, [])

  return (
    <section
      id="aggregation"
      ref={sectionRef}
      className="py-20 md:py-32 lg:py-40 bg-neutral-50/50"
      aria-labelledby="aggregation-heading"
    >
      <Container>
        <div className="text-center mb-8">
          <span
            className="label inline-block px-6 py-2 bg-primary-100 text-primary-700 rounded-full text-sm font-semibold uppercase tracking-wider"
            aria-hidden="true"
          >
            AGGREGATE
          </span>
        </div>
        <div className="text-center mb-12">
          <h2 id="aggregation-heading" className="heading-section mb-6">
            Your ingredients. Your way.
          </h2>
          <p className="body-large max-w-2xl mx-auto">
            Smart aggregation that eliminates duplicates and organizes by recipe.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8" role="list">
          {/* Recipe cards would go here */}
        </div>
        <div ref={statsRef} className="text-center mt-16">
          {/* Stats would go here */}
        </div>
        <div ref={listRef} className="mt-12">
          {/* Grocery list would go here */}
        </div>
      </Container>
    </section>
  )
}
