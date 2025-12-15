import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Material Design 3 Orange Primary Palette
        primary: {
          50: '#FFF3E0',
          100: '#FFE0B2',
          200: '#FFCC80',
          300: '#FFB74D',
          400: '#FFA726',
          500: '#FF9800', // Main orange
          600: '#FB8C00',
          700: '#F57C00',
          800: '#EF6C00',
          900: '#E65100',
          DEFAULT: '#FF6F00', // Deep Orange (primary brand color)
        },
        // Material Design 3 Grey Secondary Palette
        secondary: {
          50: '#FAFAFA',
          100: '#F5F5F5',
          200: '#EEEEEE',
          300: '#E0E0E0',
          400: '#BDBDBD',
          500: '#9E9E9E',
          600: '#757575',
          700: '#616161',
          800: '#424242',
          900: '#212121',
          DEFAULT: '#424242',
        },
        // Orange accent shades (for variety)
        orange: {
          50: '#FFF3E0',
          100: '#FFE0B2',
          200: '#FFCC80',
          300: '#FFB74D',
          400: '#FFA726',
          500: '#FF9800',
          600: '#FB8C00',
          700: '#F57C00',
          800: '#EF6C00',
          900: '#E65100',
          DEFAULT: '#FF6F00',
        },
        // Semantic colors (Material Design 3)
        success: {
          50: '#E8F5E9',
          100: '#C8E6C9',
          500: '#4CAF50',
          700: '#388E3C',
          900: '#1B5E20',
        },
        error: {
          50: '#FFEBEE',
          100: '#FFCDD2',
          500: '#F44336',
          700: '#D32F2F',
          900: '#B71C1C',
        },
        warning: {
          50: '#FFF3E0',
          100: '#FFE0B2',
          500: '#FF9800',
          700: '#F57C00',
          900: '#E65100',
        },
        info: {
          50: '#E3F2FD',
          100: '#BBDEFB',
          500: '#2196F3',
          700: '#1976D2',
          900: '#0D47A1',
        },
      },
      fontFamily: {
        sans: ['Roboto', 'Inter', 'system-ui', 'sans-serif'],
        display: ['Roboto', 'Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        'md3-xs': '4px',
        'md3-sm': '8px',
        'md3': '12px',
        'md3-lg': '16px',
        'md3-xl': '24px',
        'md3-2xl': '28px',
      },
      boxShadow: {
        // Material Design 3 Elevation System
        'md3-1': '0px 2px 4px rgba(0, 0, 0, 0.08)',
        'md3-2': '0px 4px 8px rgba(0, 0, 0, 0.12)',
        'md3-3': '0px 6px 12px rgba(0, 0, 0, 0.16)',
        'md3-4': '0px 8px 16px rgba(0, 0, 0, 0.20)',
        'md3-5': '0px 12px 24px rgba(0, 0, 0, 0.24)',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
    },
  },
  plugins: [],
}

export default config
