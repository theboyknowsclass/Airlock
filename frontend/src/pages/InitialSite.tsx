import { Box, Button, Container, Stack, Typography } from '@mui/material';
import type { Theme } from '@mui/material/styles';
import { useCallback, useMemo } from 'react';

import { ServerVersionPlaceholder } from '../components/atoms/ServerVersionPlaceholder';
import { ServerVersionBadge } from '../components/molecules/ServerVersionBadge';
import { ErrorView } from './ErrorView';
import { useServerVersion } from '../hooks/useServerVersion';
import { ServerVersionRequestError } from '../services/versionService';

const SUPPORT_CONTACT = 'mailto:support@airlock.example';

const buildErrorDetails = (error: ServerVersionRequestError) => {
  const parts = [
    `Request ID: ${error.requestId ?? error.clientRequestId}`,
    `Client Request ID: ${error.clientRequestId}`,
  ];
  if (error.status) {
    parts.push(`Status Code: ${error.status}`);
  }
  return parts;
};

const describeError = (error: ServerVersionRequestError) => {
  switch (error.type) {
    case 'timeout':
      return 'We could not retrieve the server version within one second.';
    case 'network':
      return 'A network error prevented the request from completing.';
    case 'server':
      return error.message;
    default:
      return 'An unexpected error prevented the server version from loading.';
  }
};

export function InitialSite() {
  const {
    data,
    isPending,
    isFetching,
    isError,
    error,
    refetch,
    clientRequestId,
    requestId,
  } = useServerVersion();

  const handleRetry = useCallback(() => {
    void refetch({ cancelRefetch: false });
  }, [refetch]);

  if (isError && error) {
    const detailLines = buildErrorDetails(error);

    return (
      <ErrorView
        onRetry={handleRetry}
        supportHref={SUPPORT_CONTACT}
        details={
          <Stack component="dl" spacing={1} sx={{ textAlign: 'left' }}>
            {detailLines.map((line) => {
              const [label, value] = line.split(': ');
              return (
                <Stack key={line} direction="row" spacing={1} component="div">
                  <Typography
                    component="dt"
                    variant="caption"
                    color="text.secondary"
                    sx={{ minWidth: 140, fontWeight: 600 }}
                  >
                    {label}
                  </Typography>
                  <Typography component="dd" variant="caption">
                    {value}
                  </Typography>
                </Stack>
              );
            })}
          </Stack>
        }
        description={describeError(error)}
      />
    );
  }

  const showPlaceholder = isPending || (!data && !isError);

  const versionBadge = useMemo(() => {
    if (!data) {
      return null;
    }
    return (
      <ServerVersionBadge
        label={data.displayLabel}
        retrievedAt={data.retrievedAt}
        source={data.source}
      />
    );
  }, [data]);

  const loadingPlaceholder = useMemo(
    () => (
      <ServerVersionPlaceholder
        label={
          isFetching && data
            ? 'Refreshing server version...'
            : 'Loading server version...'
        }
      />
    ),
    [data, isFetching],
  );

  return (
    <Box
      sx={{
        minHeight: '100dvh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.default',
        color: 'text.primary',
      }}
    >
      <Container
        component="main"
        maxWidth="md"
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          py: { xs: 10, md: 14 },
        }}
      >
        <Stack spacing={4}>
          <Stack spacing={1.5}>
            <Typography component="h1" variant="h2">
              Welcome to Airlock
            </Typography>
            <Typography component="p" variant="h6" color="text.secondary">
              Monitor the live server version and feel confident you are running the
              expected build.
            </Typography>
          </Stack>
          <Stack spacing={2}>
            <Typography variant="body1">
              The widget anchored to the bottom-right corner continuously fetches the
              active build identifier with a strict one-second timeout. If the request
              fails, the page transitions to an accessible error view with recovery
              options.
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Request ID:{' '}
              <Typography
                component="span"
                sx={{ fontFamily: 'Roboto Mono, monospace' }}
              >
                {requestId ?? clientRequestId ?? 'pending'}
              </Typography>
            </Typography>
          </Stack>
          <Stack direction="row" spacing={2}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={handleRetry}
              disabled={isPending}
            >
              Refresh version
            </Button>
            <Button
              variant="outlined"
              color="secondary"
              size="large"
              href={SUPPORT_CONTACT}
            >
              Contact support
            </Button>
          </Stack>
        </Stack>
      </Container>
      <Box
        component="footer"
        role="contentinfo"
        sx={{
          position: 'fixed',
          right: { xs: 16, md: 32 },
          bottom: { xs: 16, md: 32 },
          zIndex: (theme: Theme) => theme.zIndex.tooltip,
        }}
      >
        {showPlaceholder ? loadingPlaceholder : versionBadge}
      </Box>
    </Box>
  );
}
