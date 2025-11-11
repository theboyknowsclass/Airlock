import { useEffect, useMemo } from 'react';
import { Box, type BoxProps } from '@mui/material';
import type { SxProps, Theme } from '@mui/material/styles';

import {
  ErrorLayout,
  type ErrorLayoutProps,
} from '../components/organisms/ErrorLayout';

export interface ErrorViewProps
  extends Omit<ErrorLayoutProps, 'sx' | 'minHeight'> {
  documentTitle?: string;
  containerProps?: BoxProps;
}

export function ErrorView({
  documentTitle,
  containerProps,
  ...layoutProps
}: ErrorViewProps) {
  useEffect(() => {
    if (typeof document === 'undefined') {
      return;
    }

    const previousTitle = document.title;
    const nextTitle =
      documentTitle ?? 'Unable to load the server version | Airlock';
    document.title = nextTitle;

    return () => {
      document.title = previousTitle;
    };
  }, [documentTitle]);

  const baseSx = useMemo<SxProps<Theme>>(
    () => (theme: Theme) => ({
      minHeight: '100dvh',
      display: 'flex',
      flexDirection: 'column',
      bgcolor: 'background.default',
      backgroundImage: `radial-gradient(circle at 10% 20%, ${
        theme.palette.primary.light
      }22, transparent 45%), radial-gradient(circle at 90% 80%, ${
        theme.palette.error.light
      }1a, transparent 55%)`,
    }),
    [],
  );

  const combinedSx = useMemo<SxProps<Theme>>(() => {
    const overrides = containerProps?.sx;
    if (!overrides) {
      return [baseSx];
    }
    if (Array.isArray(overrides)) {
      return [baseSx, ...overrides];
    }
    return [baseSx, overrides];
  }, [baseSx, containerProps?.sx]);

  return (
    <Box
      role="presentation"
      {...containerProps}
      sx={combinedSx}
    >
      <ErrorLayout
        {...layoutProps}
        sx={{
          flex: 1,
          alignSelf: 'stretch',
        }}
      />
    </Box>
  );
}

