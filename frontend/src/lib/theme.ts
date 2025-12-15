'use client';

import { createTheme } from '@mui/material/styles';

// Material Design 3 Orange Color Palette
const orangePalette = {
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
};

// Create Material Design 3 theme with orange primary color
export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#FF6F00', // Deep Orange (Material Design 3)
      light: '#FFA726',
      dark: '#E65100',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#424242', // Grey for contrast
      light: '#616161',
      dark: '#212121',
      contrastText: '#FFFFFF',
    },
    error: {
      main: '#D32F2F',
    },
    warning: {
      main: '#F57C00',
    },
    info: {
      main: '#0288D1',
    },
    success: {
      main: '#388E3C',
    },
    background: {
      default: '#FAFAFA',
      paper: '#FFFFFF',
    },
    text: {
      primary: 'rgba(0, 0, 0, 0.87)',
      secondary: 'rgba(0, 0, 0, 0.60)',
      disabled: 'rgba(0, 0, 0, 0.38)',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Inter", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '3.5rem',
      fontWeight: 700,
      lineHeight: 1.2,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontSize: '2.75rem',
      fontWeight: 600,
      lineHeight: 1.3,
      letterSpacing: '-0.01em',
    },
    h3: {
      fontSize: '2.25rem',
      fontWeight: 600,
      lineHeight: 1.35,
    },
    h4: {
      fontSize: '1.75rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.5,
    },
    h6: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.6,
    },
    subtitle1: {
      fontSize: '1rem',
      fontWeight: 500,
      lineHeight: 1.75,
    },
    subtitle2: {
      fontSize: '0.875rem',
      fontWeight: 500,
      lineHeight: 1.57,
    },
    body1: {
      fontSize: '1rem',
      fontWeight: 400,
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      fontWeight: 400,
      lineHeight: 1.43,
    },
    button: {
      fontSize: '0.875rem',
      fontWeight: 500,
      lineHeight: 1.75,
      textTransform: 'none', // Material Design 3 uses sentence case
    },
  },
  shape: {
    borderRadius: 12, // Material Design 3 uses larger corner radius
  },
  shadows: [
    'none',
    '0px 2px 4px rgba(0, 0, 0, 0.08)', // Elevation 1
    '0px 4px 8px rgba(0, 0, 0, 0.12)', // Elevation 2
    '0px 6px 12px rgba(0, 0, 0, 0.16)', // Elevation 3
    '0px 8px 16px rgba(0, 0, 0, 0.20)', // Elevation 4
    '0px 12px 24px rgba(0, 0, 0, 0.24)', // Elevation 5
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
  ],
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 24, // Pill-shaped buttons (Material Design 3)
          padding: '10px 24px',
          fontSize: '0.875rem',
          fontWeight: 500,
          textTransform: 'none',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.12)',
          },
        },
        contained: {
          '&:hover': {
            boxShadow: '0px 6px 12px rgba(0, 0, 0, 0.16)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.08)',
          '&:hover': {
            boxShadow: '0px 8px 16px rgba(0, 0, 0, 0.12)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
        elevation1: {
          boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.08)',
        },
        elevation2: {
          boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.12)',
        },
        elevation3: {
          boxShadow: '0px 6px 12px rgba(0, 0, 0, 0.16)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
});

export default theme;
