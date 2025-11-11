import { CssBaseline, ThemeProvider } from '@mui/material';
import type { Preview } from '@storybook/react';
import { initialize, mswDecorator } from 'msw-storybook-addon';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useRef } from 'react';

import { createAppTheme } from '../src/theme';
import { defaultServerVersionHandlers } from '../src/services/versionService.mock';

initialize({
  onUnhandledRequest: 'warn',
});

const withProviders: Preview['decorators'][number] = (Story) => {
  const queryClientRef = useRef<QueryClient>();
  if (!queryClientRef.current) {
    queryClientRef.current = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          staleTime: 0,
        },
      },
    });
  }

  const themeRef = useRef(createAppTheme());

  return (
    <QueryClientProvider client={queryClientRef.current}>
      <ThemeProvider theme={themeRef.current}>
        <CssBaseline />
        <Story />
      </ThemeProvider>
    </QueryClientProvider>
  );
};

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    backgrounds: {
      default: 'dark',
      values: [
        {
          name: 'dark',
          value: '#050915',
        },
        {
          name: 'light',
          value: '#ffffff',
        },
      ],
    },
    msw: {
      handlers: [...defaultServerVersionHandlers],
    },
  },
  decorators: [mswDecorator, withProviders],
};

export default preview;

