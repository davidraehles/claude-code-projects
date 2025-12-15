'use client'

import { useState, FormEvent } from 'react'
import { motion } from 'framer-motion'
import { useMutation } from '@tanstack/react-query'
import { Container } from '../ui/container'
import { Button } from '../ui/button'
import { api } from '@/lib/api'

export function Hero() {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: (email: string) => api.joinWaitlist({
      email,
      metadata: { source: 'hero' }
    }),
    onSuccess: () => {
      setSubmitted(true)
      setEmail('')
      setError(null)
    },
    onError: (err: Error) => {
      setError(err.message || 'An unexpected error occurred')
    }
  })

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!email.trim()) return

    mutation.mutate(email.trim())
  }

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: 'spring' as const,
        stiffness: 100,
        damping: 20,
      },
    },
  }

  const headlineVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        type: 'spring' as const,
        stiffness: 100,
        damping: 20,
        delay: 0.3,
      },
    },
  }

  const scrollIndicatorVariants = {
    hidden: { opacity: 0, y: -20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        delay: 1,
        duration: 0.6,
        repeat: Infinity,
        repeatType: 'reverse' as const,
        repeatDelay: 0.5,
      },
    },
  }

  return (
    <section id="hero" className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 to-orange-500 text-white relative overflow-hidden py-12">
      <Container className="text-center">
        <motion.div
          className="max-w-4xl mx-auto"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Logo */}
          <motion.h2
            className="text-4xl md:text-6xl lg:text-7xl font-black mb-12 bg-gradient-to-r from-white to-neutral-100 bg-clip-text text-transparent drop-shadow-2xl"
            variants={itemVariants}
          >
            Go, Cart!
          </motion.h2>

          {/* Headline */}
          <motion.h1
            className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-black leading-tight mb-12 max-w-3xl mx-auto tracking-tight"
            variants={headlineVariants}
          >
            Favorites on repeat.
            <br />
            New loves on deck.
            <br />
            Groceries on autopilot.
          </motion.h1>

          {/* Waitlist Form */}
          {!submitted ? (
            <motion.form
              onSubmit={handleSubmit}
              className="flex flex-col sm:flex-row gap-4 justify-center max-w-md mx-auto mb-16"
              variants={itemVariants}
            >
              <label htmlFor="waitlist-email" className="sr-only">
                Email address
              </label>
              <motion.input
                id="waitlist-email"
                type="email"
                placeholder="Enter your email to join the waitlist"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="flex-1 px-6 py-4 text-lg rounded-xl bg-white/20 backdrop-blur-md border border-white/30 focus:border-white focus:outline-none placeholder:text-white/70 transition-all"
                required
                disabled={mutation.isPending}
                aria-label="Email address"
                whileFocus={{ scale: 1.02 }}
              />
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button
                  type="submit"
                  className="px-12 py-4 text-xl font-semibold shadow-2xl shadow-primary-900/50 hover:shadow-primary/50 hover:-translate-y-1 whitespace-nowrap"
                  disabled={mutation.isPending || !email.trim()}
                  aria-busy={mutation.isPending}
                >
                  {mutation.isPending ? 'Joining...' : 'Join Waitlist'}
                </Button>
              </motion.div>
            </motion.form>
          ) : (
            <motion.div
              className="max-w-md mx-auto mb-16 p-8 bg-white/10 backdrop-blur-md rounded-2xl border border-white/20"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ type: 'spring', stiffness: 200, damping: 25 }}
            >
              <h3 className="text-2xl font-bold mb-4">🎉 Thanks for joining the waitlist!</h3>
              <p className="text-lg">We'll be in touch soon.</p>
              <Button
                className="mt-6"
                onClick={() => setSubmitted(false)}
              >
                Join another?
              </Button>
            </motion.div>
          )}

          {error && (
            <motion.div
              role="alert"
              className="text-red-200 text-lg mb-16 max-w-md mx-auto bg-red-500/20 p-4 rounded-xl border border-red-400/50 flex items-center gap-4"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <p className="flex-1">{error}</p>
              <Button
                className="ml-4 px-3 py-1 flex-shrink-0"
                onClick={() => setError(null)}
                aria-label="Dismiss error"
              >
                Dismiss
              </Button>
            </motion.div>
          )}

          {/* Scroll indicator */}
          <motion.div
            className="text-4xl"
            variants={scrollIndicatorVariants}
            initial="hidden"
            animate="visible"
            role="img"
            aria-label="Scroll down to see more"
          >
            ↓
          </motion.div>
        </motion.div>
      </Container>
    </section>
  )
}
