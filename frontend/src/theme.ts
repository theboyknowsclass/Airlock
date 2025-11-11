import { createTheme, responsiveFontSizes } from '@mui/material/styles';
import type { Theme } from '@mui/material/styles';

export const createAppTheme = (): Theme =>
  responsiveFontSizes(
    createTheme({
      palette: {
        mode: 'dark',
        primary: {
          main: '#4F9CF9',
        },
        secondary: {
          main: '#F98C4F',
        },
        background: {
          default: '#050915',
          paper: '#0D152A',
        },
      },
      typography: {
        fontFamily: '"Inter", "Helvetica Neue", Arial, sans-serif',
        h1: {
          fontWeight: 700,
          letterSpacing: 0.5,
        },
        h2: {
          fontWeight: 700,
          letterSpacing: 0.5,
        },
      },
      shape: {
        borderRadius: 12,
      },
      components: {
        MuiButton: {
          styleOverrides: {
            root: {
              textTransform: 'none',
              fontWeight: 600,
            },
          },
        },
      },
    }),
  );

