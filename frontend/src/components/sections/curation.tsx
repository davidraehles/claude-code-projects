'use client'

import { Container } from '../ui/container'

const recipeCards = [
  {
    title: `Ottolenghi's Roasted Ratatouille`,
    image: 'https://images.unsplash.com/photo-1572453800999-e8d2d1589b7c?w=400&h=300&fit=crop&auto=format',
    meta: ['Vegan', '30 min', 'Serves 4']
  },
  {
    title: 'Creamy Mushroom Risotto',
    image: 'https://images.unsplash.com/photo-1476124369491-e7addf5db371?w=400&h=300&fit=crop&auto=format',
    meta: ['Vegetarian', '45 min', 'Serves 2']
  },
  {
    title: 'Spicy Thai Basil Chicken',
    image: 'https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=400&h=300&fit=crop&auto=format',
    meta: ['Gluten-free', '20 min', 'Serves 3']
  },
  {
    title: 'Lemon Garlic Shrimp Pasta',
    image: 'https://images.unsplash.com/photo-1473093295043-cdd812d0e601?w=400&h=300&fit=crop&auto=format',
    meta: ['Quick', '25 min', 'Serves 4']
  },
  {
    title: 'Baked Feta Pasta',
    image: 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9d9?w=400&h=300&fit=crop&auto=format',
    meta: ['Viral', '40 min', 'Serves 6']
  },
  {
    title: 'Korean Bibimbap Bowl',
    image: 'https://images.unsplash.com/photo-1553163147-622ab57be1c7?w=400&h=300&fit=crop&auto=format',
    meta: ['Healthy', '35 min', 'Serves 2']
  }
]

export function Curation() {
  return (
    <section id="curation" className="py-20 md:py-32 lg:py-40 bg-neutral-50/50" aria-labelledby="curation-heading">
      <Container>
        {/* Section Label */}
        <div className="text-center mb-8">
          <span className="label inline-block px-6 py-2 bg-primary-100 text-primary-700 rounded-full text-sm font-semibold uppercase tracking-wider" aria-hidden="true">
            CURATE
          </span>
        </div>

        {/* Headline */}
        <div className="text-center mb-12">
          <h2 id="curation-heading" className="heading-section mb-6">Your recipes. Your way.</h2>
          <p className="body-large max-w-2xl mx-auto">
            Save recipes from anywhere. Build your personal cookbook.
          </p>
        </div>

        {/* Recipe Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8" role="list">
          {recipeCards.map((card, index) => (
            <article
              key={index}
              className="group recipe-card bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl hover:-translate-y-4 transition-all duration-500 cursor-pointer border border-neutral-200 hover:border-primary-200"
              role="listitem"
            >
              <div
                className="w-full h-64 bg-gradient-to-br from-neutral-200 to-neutral-300 group-hover:scale-105 transition-transform duration-500"
                style={{ backgroundImage: `url(${card.image})`, backgroundSize: 'cover', backgroundPosition: 'center' }}
                role="img"
                aria-label={`Photo of ${card.title}`}
              />
              <div className="p-6">
                <h3 className="heading-card mb-4 group-hover:text-primary-600 transition-colors">{card.title}</h3>
                <div className="flex flex-wrap gap-2" role="list" aria-label={`Recipe details for ${card.title}`}>
                  {card.meta.map((tag, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 bg-neutral-100 text-neutral-600 text-xs rounded-full font-medium"
                      role="listitem"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </article>
          ))}
        </div>
      </Container>
    </section>
  )
}
