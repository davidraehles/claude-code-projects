'use client'

import { useState, FormEvent } from 'react'
import { Container } from '../ui/container'
import { Button } from '../ui/button'

export function Hero() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!email.trim()) return

    setLoading(true)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/v1/waitlist`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email.trim(),
          metadata: {
            source: 'hero',
          },
        }),
      })

      if (!response.ok) {
        const data = await response.json().catch(() => ({}))
        throw new Error(data.detail || 'Failed to join waitlist')
      }

      setSubmitted(true)
      setEmail('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 to-orange-500 text-white relative overflow-hidden py-12">
      <Container className="text-center">
        <div className="max-w-4xl mx-auto">
          {/* Logo */}
          <h2 className="text-4xl md:text-6xl lg:text-7xl font-black mb-12 bg-gradient-to-r from-white to-neutral-100 bg-clip-text text-transparent drop-shadow-2xl">
            Go, Cart!
          </h2>

          {/* Headline */}
          <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-black leading-tight mb-12 max-w-3xl mx-auto tracking-tight">
            Favorites on repeat.
            <br />
            New loves on deck.
            <br />
            Groceries on autopilot.
          </h1>

          {/* Waitlist Form */}
          {!submitted ? (
            <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-4 justify-center max-w-md mx-auto mb-16">
              <label htmlFor="waitlist-email" className="sr-only">
                Email address
              </label>
              <input
                id="waitlist-email"
                type="email"
                placeholder="Enter your email to join the waitlist"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="flex-1 px-6 py-4 text-lg rounded-xl bg-white/20 backdrop-blur-md border border-white/30 focus:border-white focus:outline-none placeholder:text-white/70"
                required
                disabled={loading}
                aria-label="Email address"
              />
              <Button
                type="submit"
                className="px-12 py-4 text-xl font-semibold shadow-2xl shadow-primary-900/50 hover:shadow-primary/50 hover:-translate-y-1 whitespace-nowrap"
                disabled={loading || !email.trim()}
                aria-busy={loading}
              >
                {loading ? 'Joining...' : 'Join Waitlist'}
              </Button>
            </form>
          ) : (
            <div className="max-w-md mx-auto mb-16 p-8 bg-white/10 backdrop-blur-md rounded-2xl border border-white/20">
              <h3 className="text-2xl font-bold mb-4">🎉 Welcome to the waitlist!</h3>
              <p className="text-lg">Check your email to verify and secure your spot.</p>
              <Button
                className="mt-6"
                onClick={() => setSubmitted(false)}
              >
                Join another?
              </Button>
            </div>
          )}

          {error && (
            <div role="alert" className="text-red-200 text-lg mb-16 max-w-md mx-auto bg-red-500/20 p-4 rounded-xl border border-red-400/50 flex items-center gap-4">
              <p className="flex-1">{error}</p>
              <Button
                className="ml-4 px-3 py-1 flex-shrink-0"
                onClick={() => setError(null)}
                aria-label="Dismiss error"
              >
                Dismiss
              </Button>
            </div>
          )}

          {/* Scroll indicator */}
          <div className="text-4xl animate-bounce">↓</div>
        </div>
      </Container>
    </section>
  )
}
