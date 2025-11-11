import {
  Box,
  Button,
  Container,
  Link,
  Stack,
  Typography,
  type BoxProps,
} from '@mui/material';
import { useEffect, useId, useMemo, useRef } from 'react';
import type { ReactNode } from 'react';

const DEFAULT_TITLE = 'We cannot load the server version.';
const DEFAULT_DESCRIPTION =
  'The request took longer than expected. Please try again or reach out to support if the issue persists.';
const DEFAULT_RETRY_LABEL = 'Try again';
const DEFAULT_SUPPORT_LABEL = 'Contact support';

export interface ErrorLayoutProps extends Omit<BoxProps, 'children'> {
  title?: string;
  description?: ReactNode;
  retryLabel?: string;
  supportHref?: string;
  supportLabel?: string;
  onRetry?: () => void;
  details?: ReactNode;
}

export function ErrorLayout({
  title = DEFAULT_TITLE,
  description = DEFAULT_DESCRIPTION,
  retryLabel = DEFAULT_RETRY_LABEL,
  supportHref,
  supportLabel = DEFAULT_SUPPORT_LABEL,
  onRetry,
  details,
  sx,
  ...rest
}: ErrorLayoutProps) {
  const focusRef = useRef<HTMLDivElement>(null);
  const headingId = useId();
  const descriptionId = useId();

  useEffect(() => {
    const node = focusRef.current;
    if (node) {
      node.focus();
    }
  }, []);

  const resolvedDescription = useMemo(() => {
    if (typeof description === 'string') {
      return (
        <Typography
          variant="body1"
          color="text.secondary"
          id={descriptionId}
          sx={{ maxWidth: 540 }}
        >
          {description}
        </Typography>
      );
    }

    return (
      <Box id={descriptionId} sx={{ maxWidth: 540 }}>
        {description}
      </Box>
    );
  }, [description, descriptionId]);

  return (
    <Box
      ref={focusRef}
      role="alert"
      aria-live="assertive"
      aria-labelledby={headingId}
      aria-describedby={descriptionId}
      tabIndex={-1}
      sx={{
        outline: 'none',
        display: 'flex',
        minHeight: '100%',
        width: '100%',
        alignItems: 'center',
        justifyContent: 'center',
        px: { xs: 2, sm: 4 },
        py: { xs: 6, sm: 10 },
        ...sx,
      }}
      {...rest}
    >
      <Container maxWidth="sm">
        <Stack
          spacing={3}
          alignItems="center"
          justifyContent="center"
          textAlign="center"
        >
          <Typography
            id={headingId}
            component="h1"
            variant="h3"
            sx={{ fontWeight: 700, letterSpacing: 0.5 }}
          >
            {title}
          </Typography>
          {resolvedDescription}
          {details && (
            <Box
              role="presentation"
              sx={{
                maxWidth: 520,
                color: 'text.secondary',
              }}
            >
              {details}
            </Box>
          )}
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={2}
            alignItems="center"
            justifyContent="center"
          >
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={onRetry}
            >
              {retryLabel}
            </Button>
            {supportHref && (
              <Button
                component={Link}
                href={supportHref}
                variant="text"
                color="inherit"
                size="large"
              >
                {supportLabel}
              </Button>
            )}
          </Stack>
        </Stack>
      </Container>
    </Box>
  );
}

