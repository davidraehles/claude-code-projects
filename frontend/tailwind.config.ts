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
        primary: {
          50: '#FFF5F4',
          100: '#FFE5E3',
          200: '#FFCCC7',
          300: '#FFA69E',
          400: '#FF7A6F',
          500: '#E85A4F',
          600: '#D04439',
          700: '#AE3328',
          800: '#902B22',
          900: '#772922',
        },
        secondary: {
          50: '#F4F5F7',
          100: '#E4E7EB',
          200: '#CBD2D9',
          300: '#9AA5B1',
          400: '#616E7C',
          500: '#3
