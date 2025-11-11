import { forwardRef } from 'react';
import {
  Box,
  Skeleton,
  Typography,
  type BoxProps,
} from '@mui/material';

const DEFAULT_LABEL = 'Loading server version...';

export interface ServerVersionPlaceholderProps
  extends Omit<BoxProps, 'children'> {
  label?: string;
}

export const ServerVersionPlaceholder = forwardRef<
  HTMLDivElement,
  ServerVersionPlaceholderProps
>(function ServerVersionPlaceholder(
  { label = DEFAULT_LABEL, sx, ...rest },
  ref,
) {
  return (
    <Box
      ref={ref}
      role="status"
      aria-live="polite"
      aria-busy="true"
      aria-label={label}
      sx={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 1,
        px: 1.5,
        py: 0.75,
        borderRadius: 2,
        bgcolor: 'grey.900',
        color: 'common.white',
        boxShadow: 4,
        fontWeight: 600,
        letterSpacing: 0.4,
        ...sx,
      }}
      {...rest}
    >
      <Skeleton
        variant="rounded"
        animation="pulse"
        height={16}
        width={16}
        sx={{ borderRadius: '50%' }}
        aria-hidden="true"
        role={undefined}
      />
      <Typography
        component="span"
        variant="body2"
        sx={{ fontWeight: 600, textTransform: 'uppercase' }}
      >
        {label}
      </Typography>
    </Box>
  );
});

