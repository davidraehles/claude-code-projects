/**
 * Card component for content containers with Material Design 3 styling.
 */

import React from 'react'
import { cn } from '@/lib/utils'

interface CardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
  elevation?: 1 | 2 | 3 | 4 | 5
  variant?: 'elevated' | 'filled' | 'outlined'
  onClick?: () => void
}

export function Card({ 
  children, 
  className = '', 
  hover = false, 
  elevation = 2,
  variant = 'elevated',
  onClick 
}: CardProps) {
  const baseStyles = 'rounded-md3-lg transition-all duration-300'
  const hoverStyles = hover ? 'hover:shadow-md3-4 hover:-translate-y-1 cursor-pointer' : ''
  
  const variantStyles = {
    elevated: `bg-white shadow-md3-${elevation}`,
    filled: 'bg-primary-50 shadow-none',
    outlined: 'bg-white border-2 border-secondary-300 shadow-none'
  }

  return (
    <div
      className={cn(
        baseStyles,
        variantStyles[variant],
        hoverStyles,
        'p-6',
        className
      )}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onClick()
        }
      } : undefined}
    >
      {children}
    </div>
  )
}

export function CardHeader({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn('mb-4', className)}>
      {children}
    </div>
  )
}

export function CardTitle({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <h3 className={cn('text-headline-medium font-semibold text-secondary-900', className)}>
      {children}
    </h3>
  )
}

export function CardDescription({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <p className={cn('text-body-medium text-secondary-700 mt-2', className)}>
      {children}
    </p>
  )
}

export function CardContent({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn('text-body-large', className)}>
      {children}
    </div>
  )
}

export function CardActions({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn('mt-6 flex gap-3 items-center', className)}>
      {children}
    </div>
  )
}
