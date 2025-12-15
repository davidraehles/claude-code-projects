/**
 * Input component with Material Design 3 styling.
 */

import { forwardRef, InputHTMLAttributes, ReactNode } from 'react'
import { cn } from '@/lib/utils'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
  variant?: 'outlined' | 'filled'
  icon?: ReactNode
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, type = 'text', label, error, helperText, variant = 'outlined', icon, ...props }, ref) => {
    const inputId = props.id || props.name || `input-${Math.random().toString(36).substr(2, 9)}`
    
    const variantStyles = {
      outlined: 'border-2 border-secondary-300 bg-transparent hover:border-primary focus:border-primary focus:border-2',
      filled: 'border-0 border-b-2 border-secondary-300 bg-secondary-100 hover:border-primary focus:border-primary focus:bg-secondary-200'
    }

    return (
      <div className="w-full">
        {label && (
          <label 
            htmlFor={inputId}
            className="block text-body-medium font-medium text-secondary-900 mb-2"
          >
            {label}
            {props.required && <span className="text-error-500 ml-1" aria-label="required">*</span>}
          </label>
        )}
        <div className="relative">
          {icon && (
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-secondary-500">
              {icon}
            </div>
          )}
          <input
            id={inputId}
            type={type}
            className={cn(
              'flex h-12 w-full rounded-md3 py-3 text-body-large transition-colors',
              icon ? 'pl-12 pr-4' : 'px-4',
              'placeholder:text-secondary-500',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-1',
              'disabled:cursor-not-allowed disabled:opacity-38',
              variantStyles[variant],
              error && 'border-error-500 focus:border-error-500 focus:ring-error-500',
              className
            )}
            ref={ref}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={
              error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined
            }
            {...props}
          />
        </div>
        {error && (
          <p 
            id={`${inputId}-error`}
            className="mt-2 text-body-medium text-error-700"
            role="alert"
          >
            {error}
          </p>
        )}
        {helperText && !error && (
          <p 
            id={`${inputId}-helper`}
            className="mt-2 text-body-medium text-secondary-600"
          >
            {helperText}
          </p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export { Input }
