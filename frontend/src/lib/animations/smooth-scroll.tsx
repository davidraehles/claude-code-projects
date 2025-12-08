'use client'

import { useEffect } from 'react'
import Lenis from '@studio-freight/lenis'

/**
 * SmoothScrollProvider - Initializes and manages Lenis smooth scrolling
 *
 * Features:
 * - Smooth, buttery scrolling with easing
 * - 60fps performance optimized
 * - Mobile-responsive (reduced on touch devices)
 * - Respects prefers-reduced-motion
 *
 * Usage: Wrap your layout or page with this provider
 */
export function SmoothScrollProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    if (prefersReducedMotion) {
      return // Don't apply smooth scroll if user prefers reduced motion
    }

    // Initialize Lenis
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), // Custom easing function
      orientation: 'vertical',
      gestureOrientation: 'vertical',
      smoothWheel: true,
      wheelMultiplier: 1,
      touchMultiplier: 2,
      infinite: false,
    })

    // Animation frame loop
    function raf(time: number) {
      lenis.raf(time)
      requestAnimationFrame(raf)
    }
    requestAnimationFrame(raf)

    // Cleanup
    return () => {
      lenis.destroy()
    }
  }, [])

  return <>{children}</>
}

/**
 * useLenisScroll - Custom hook to access Lenis instance
 *
 * Use this hook to programmatically control scroll behavior
 *
 * Example:
 * const { scrollTo } = useLenisScroll()
 * scrollTo('#section-id', { duration: 2 })
 */
export function useLenisScroll() {
  const scrollTo = (target: string | number, options?: { duration?: number; offset?: number }) => {
    const lenis = (window as { lenis?: Lenis }).lenis

    if (lenis) {
      lenis.scrollTo(target, {
        duration: options?.duration,
        offset: options?.offset,
      })
    } else {
      // Fallback for when Lenis isn't initialized
      if (typeof target === 'string') {
        const element = document.querySelector(target)
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' })
        }
      } else {
        window.scrollTo({ top: target, behavior: 'smooth' })
      }
    }
  }

  return { scrollTo }
}
