import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Curation } from '@/components/sections/curation'

describe('Curation Component', () => {
  beforeEach(() => {
    render(<Curation />)
  })

  describe('Section Content', () => {
    it('renders the CURATE label', () => {
      expect(screen.getByText('CURATE')).toBeInTheDocument()
    })

    it('renders the main headline', () => {
      expect(screen.getByRole('heading', { name: 'Your recipes. Your way.' })).toBeInTheDocument()
    })

    it('renders the subtitle', () => {
      expect(screen.getByText('Save recipes from anywhere. Build your personal cookbook.')).toBeInTheDocument()
    })
  })

  describe('Recipe Cards', () => {
    it('renders 6 recipe cards', () => {
      const articles = screen.getAllByRole('listitem')
      // 6 recipe cards + multiple meta tags per card
      expect(articles.length).toBeGreaterThanOrEqual(6)
    })

    it('renders Ottolenghi\'s Roasted Ratatouille', () => {
      expect(screen.getByRole('heading', { name: "Ottolenghi's Roasted Ratatouille" })).toBeInTheDocument()
    })

    it('renders Creamy Mushroom Risotto', () => {
      expect(screen.getByRole('heading', { name: 'Creamy Mushroom Risotto' })).toBeInTheDocument()
    })

    it('renders Spicy Thai Basil Chicken', () => {
      expect(screen.getByRole('heading', { name: 'Spicy Thai Basil Chicken' })).toBeInTheDocument()
    })

    it('renders Lemon Garlic Shrimp Pasta', () => {
      expect(screen.getByRole('heading', { name: 'Lemon Garlic Shrimp Pasta' })).toBeInTheDocument()
    })

    it('renders Baked Feta Pasta', () => {
      expect(screen.getByRole('heading', { name: 'Baked Feta Pasta' })).toBeInTheDocument()
    })

    it('renders Korean Bibimbap Bowl', () => {
      expect(screen.getByRole('heading', { name: 'Korean Bibimbap Bowl' })).toBeInTheDocument()
    })
  })

  describe('Recipe Images', () => {
    it('recipe cards have image containers with Unsplash URLs', () => {
      // Check that recipe cards have the background image divs
      const imageContainers = document.querySelectorAll('div[role="img"]')
      expect(imageContainers.length).toBe(6)

      // Check that at least one has the expected Unsplash URL format
      const hasUnsplashImage = Array.from(imageContainers).some(
        container => container.getAttribute('style')?.includes('images.unsplash.com')
      )
      expect(hasUnsplashImage).toBe(true)
    })

    it('image containers have proper aria-labels', () => {
      const ratatouilleImage = screen.getByRole('img', { name: "Photo of Ottolenghi's Roasted Ratatouille" })
      expect(ratatouilleImage).toBeInTheDocument()
    })
  })

  describe('Recipe Metadata', () => {
    it('displays dietary tags for recipes', () => {
      expect(screen.getByText('Vegan')).toBeInTheDocument()
      expect(screen.getByText('Vegetarian')).toBeInTheDocument()
      expect(screen.getByText('Gluten-free')).toBeInTheDocument()
    })

    it('displays cooking times', () => {
      expect(screen.getByText('30 min')).toBeInTheDocument()
      expect(screen.getByText('45 min')).toBeInTheDocument()
      expect(screen.getByText('20 min')).toBeInTheDocument()
    })

    it('displays serving sizes', () => {
      expect(screen.getAllByText(/Serves \d/).length).toBeGreaterThan(0)
    })
  })
})
