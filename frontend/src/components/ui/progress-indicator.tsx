'use client'

import { useEffect, useState } from 'react'
import { motion, useScroll, useSpring } from 'framer-motion'

type Section = {
  id: string
  label: string
}

const sections: Section[] = [
  { id: 'hero', label: 'Hero' },
  { id: 'curation', label: 'Curate' },
  { id: 'planning', label: 'Plan' },
  { id: 'aggregation', label: 'Aggregate' },
  { id: 'checkout', label: 'Order' },
  { id: 'footer', label: 'Get Started' },
]

/**
 * ScrollProgressIndicator - Shows scroll progress through page sections
 *
 * Features:
 * - Vertical dot navigation on desktop
 * - Horizontal progress bar on mobile
 * - Auto-detects active section based on scroll position
 * - Smooth scroll to section on click
 * - Respects prefers-reduced-motion
 *
 * Usage: Place once in layout, typically at root level
 */
export function ScrollProgressIndicator() {
  const [activeSection, setActiveSection] = useState(0)
  const [isVisible, setIsVisible] = useState(false)
  const { scrollYProgress } = useScroll()
  const scaleX = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001,
  })

  useEffect(() => {
    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (prefersReducedMotion) return

    // Show indicator after initial scroll
    const handleScroll = () => {
      if (window.scrollY > 100) {
        setIsVisible(true)
      } else {
        setIsVisible(false)
      }

      // Determine active section
      const scrollPosition = window.scrollY + window.innerHeight / 2
      const documentHeight = document.documentElement.scrollHeight

      sections.forEach((section, index) => {
        const element = document.getElementById(section.id)
        if (element) {
          const { offsetTop, offsetHeight } = element
          if (scrollPosition >= offsetTop && scrollPosition < offsetTop + offsetHeight) {
            setActiveSection(index)
          }
        }
      })

      // Handle last section (footer)
      if (scrollPosition >= documentHeight - window.innerHeight) {
        setActiveSection(sections.length - 1)
      }
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    handleScroll() // Initial check

    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  if (!isVisible) return null

  return (
    <>
      {/* Desktop: Vertical Dot Navigation */}
      <motion.nav
        className="hidden lg:flex fixed top-1/2 right-6 xl:right-10 -translate-y-1/2 flex-col gap-4 z-50"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6 }}
        aria-label="Page sections"
      >
        {sections.map((section, index) => (
          <button
            key={section.id}
            onClick={() => scrollToSection(section.id)}
            className="group relative"
            aria-label={`Go to ${section.label}`}
            aria-current={activeSection === index ? 'true' : 'false'}
          >
            {/* Dot */}
            <motion.div
              className={`w-3 h-3 rounded-full transition-colors ${
                activeSection === index
                  ? 'bg-primary-500'
                  : 'bg-neutral-400 hover:bg-primary-400'
              }`}
              animate={{
                scale: activeSection === index ? 1.3 : 1,
              }}
              transition={{ type: 'spring', stiffness: 300, damping: 25 }}
            />

            {/* Tooltip */}
            <span className="absolute right-6 top-1/2 -translate-y-1/2 px-3 py-1.5 bg-secondary-800 text-white text-sm font-medium rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
              {section.label}
            </span>
          </button>
        ))}
      </motion.nav>

      {/* Mobile: Horizontal Progress Bar */}
      <motion.div
        className="lg:hidden fixed top-0 left-0 right-0 h-1 bg-neutral-200 z-50"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <motion.div
          className="h-full bg-gradient-to-r from-primary-500 to-orange-500 origin-left"
          style={{ scaleX }}
        />
      </motion.div>

      {/* Mobile: Section Counter */}
      <motion.div
        className="lg:hidden fixed bottom-6 right-6 px-4 py-2 bg-secondary-800/90 backdrop-blur-md text-white rounded-full text-sm font-medium shadow-lg z-50"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {activeSection + 1} / {sections.length}
      </motion.div>
    </>
  )
}

/**
 * Alternative: Circular Progress Indicator
 *
 * A circular progress indicator that can be used instead of or alongside the dot navigation
 */
export function CircularProgressIndicator() {
  const { scrollYProgress } = useScroll()
  const circumference = 2 * Math.PI * 20 // radius = 20

  return (
    <motion.div
      className="fixed bottom-6 left-6 w-12 h-12 z-50"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
    >
      <svg width="48" height="48" viewBox="0 0 48 48" className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx="24"
          cy="24"
          r="20"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          className="text-neutral-300"
        />
        {/* Progress circle */}
        <motion.circle
          cx="24"
          cy="24"
          r="20"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          className="text-primary-500"
          style={{
            pathLength: scrollYProgress,
          }}
          strokeDasharray={circumference}
          strokeDashoffset={0}
        />
      </svg>
    </motion.div>
  )
}
