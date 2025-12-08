import { Hero } from '@/components/sections/hero'
import { Curation } from '@/components/sections/curation'
import { Planning } from '@/components/sections/planning'
import { Aggregation } from '@/components/sections/aggregation'
import { Checkout } from '@/components/sections/checkout'
import { Footer } from '@/components/sections/footer'

export const metadata = {
  title: 'Go, Cart! - Favorites on repeat. Groceries on autopilot.',
  description: 'Smart meal curation, effortless planning, and automatic grocery aggregation. Join the waitlist.',
}

export default function LandingPage() {
  return (
    <>
      <Hero />
      <main id="main-content">
        <Curation />
        <Planning />
        <Aggregation />
        <Checkout />
      </main>
      <Footer />
    </>
  )
}
