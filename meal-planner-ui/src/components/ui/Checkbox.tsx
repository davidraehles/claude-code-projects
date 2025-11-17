/**
 * Checkbox component for forms.
 */

import React from 'react'

interface CheckboxProps {
  label: string
  checked: boolean
  onChange: (checked: boolean) => void
  disabled?: boolean
}

export function Checkbox({ label, checked, onChange, disabled = false }: CheckboxProps) {
  return (
    <label className="flex items-center space-x-3 cursor-pointer group">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        disabled={disabled}
        className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <span className={`text-sm ${disabled ? 'text-gray-400' : 'text-gray-700 group-hover:text-gray-900'}`}>
        {label}
      </span>
    </label>
  )
}
