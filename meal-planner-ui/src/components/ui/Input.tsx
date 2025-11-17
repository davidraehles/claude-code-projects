/**
 * Input component for forms and search.
 */

import React from 'react'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  icon?: React.ReactNode
}

export function Input({
  label,
  error,
  icon,
  className = '',
  ...props
}: InputProps) {
  const baseStyles = 'w-full px-4 py-2.5 border rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500'
  const errorStyles = error ? 'border-red-500' : 'border-gray-300'
  const iconPadding = icon ? 'pl-10' : ''

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            {icon}
          </div>
        )}
        <input
          className={`${baseStyles} ${errorStyles} ${iconPadding} ${className}`}
          {...props}
        />
      </div>
      {error && (
        <p className="mt-1.5 text-sm text-red-600">{error}</p>
      )}
    </div>
  )
}
