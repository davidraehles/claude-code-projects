'use client'

import { lazy, Suspense } from 'react'
import { Container } from '../ui/container'

// Dynamically import the heavy aggregation component
const AggregationComponent = lazy(() => import('./aggregation').then(module => ({ default: module.Aggregation })))

/**
 * Dynamically loaded Aggregation section with code splitting
 * Reduces initial bundle size by loading GSAP only when needed
 */
export function AggregationDynamic() {
  return (
    <Suspense fallback={<AggregationFallback />}>
      <AggregationComponent />
    </Suspense>
  )
}

/**
 * Fallback component shown while loading
 */
function AggregationFallback() {
  return (
    <section id="aggregation" className="py-20 md:py-32 lg:py-40 bg-neutral-50/50" aria-labelledby="aggregation-heading">
      <Container>
        <div className="text-center mb-8">
          <span className="label inline-block px-6 py-2 bg-primary-100 text-primary-700 rounded-full text-sm font-semibold uppercase tracking-wider" aria-hidden="true">
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 animate-pulse">
          {[1, 2, 3].map((item) => (
            <div key={item} className="recipe-card bg-white rounded-2xl overflow-hidden shadow-lg border border-neutral-200 h-96">
              <div className="w-full h-64 bg-gradient-to-br from-neutral-200 to-neutral-300"></div>
              <div className="p-6">
                <div className="h-6 bg-neutral-200 rounded mb-4"></div>
                <div className="flex flex-wrap gap-2">
                  <div className="h-4 bg-neutral-100 rounded w-16"></div>
                  <div className="h-4 bg-neutral-100 rounded w-12"></div>
                  <div className="h-4 bg-neutral-100 rounded w-10"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Container>
    </section>
  )
}
