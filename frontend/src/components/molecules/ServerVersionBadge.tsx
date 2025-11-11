import { forwardRef, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  type PaperProps,
} from '@mui/material';
import { visuallyHidden } from '@mui/utils';

const DEFAULT_TITLE = 'Server version';

export interface ServerVersionBadgeProps
  extends Omit<PaperProps, 'children'> {
  label: string;
  retrievedAt?: string;
  source?: string;
}

const formatTimestamp = (value?: string): string | undefined => {
  if (!value) {
    return undefined;
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return undefined;
  }

  return date.toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  });
};

export const ServerVersionBadge = forwardRef<
  HTMLDivElement,
  ServerVersionBadgeProps
>(function ServerVersionBadge(
  { label, retrievedAt, source, sx, ...rest },
  ref,
) {
  const formattedRetrievedAt = useMemo(
    () => formatTimestamp(retrievedAt),
    [retrievedAt],
  );

  const announcement = useMemo(() => {
    if (!formattedRetrievedAt && !source) {
      return `${DEFAULT_TITLE}: ${label}`;
    }

    const parts = [`${DEFAULT_TITLE}: ${label}`];
    if (formattedRetrievedAt) {
      parts.push(`retrieved ${formattedRetrievedAt}`);
    }
    if (source) {
      parts.push(`source ${source}`);
    }
    return parts.join(', ');
  }, [formattedRetrievedAt, label, source]);

  return (
    <Paper
      ref={ref}
      role="status"
      aria-live="polite"
      aria-label={announcement}
      elevation={6}
      sx={{
        display: 'inline-flex',
        flexDirection: 'column',
        gap: 0.25,
        px: 1.5,
        py: 1,
        borderRadius: 2,
        bgcolor: 'success.main',
        color: 'common.white',
        boxShadow: 6,
        minWidth: 0,
        ...sx,
      }}
      {...rest}
    >
      <Typography
        component="span"
        variant="caption"
        sx={{
          fontWeight: 600,
          letterSpacing: 0.6,
          textTransform: 'uppercase',
          opacity: 0.9,
        }}
      >
        {DEFAULT_TITLE}
      </Typography>
      <Typography
        component="span"
        variant="body1"
        sx={{
          fontFamily: 'Roboto Mono, monospace',
          fontWeight: 600,
          letterSpacing: 0.5,
          whiteSpace: 'nowrap',
        }}
      >
        {label}
      </Typography>
      {(formattedRetrievedAt || source) && (
        <Box
          component="span"
          sx={{
            display: 'flex',
            gap: 0.5,
            alignItems: 'center',
          }}
        >
          {formattedRetrievedAt && (
            <Typography
              component="span"
              variant="caption"
              color="common.white"
              sx={{ opacity: 0.85 }}
            >
              {formattedRetrievedAt}
            </Typography>
          )}
          {source && (
            <Typography
              component="span"
              variant="caption"
              color="common.white"
              sx={{ opacity: 0.85 }}
            >
              {source}
            </Typography>
          )}
        </Box>
      )}
      <Typography component="span" sx={visuallyHidden}>
        {announcement}
      </Typography>
    </Paper>
  );
});

