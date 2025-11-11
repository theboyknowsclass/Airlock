import { CssBaseline, ThemeProvider } from '@mui/material';
import {
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query';
import {
  render,
  renderHook,
  type RenderHookOptions,
  type RenderOptions,
} from '@testing-library/react';
import type { ReactElement, ReactNode } from 'react';

import { createAppTheme } from '../theme';

export const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: Infinity,
      },
    },
  });

export interface ProvidersOptions {
  queryClient?: QueryClient;
}

const Providers = ({
  children,
  queryClient,
}: {
  children: ReactNode;
  queryClient: QueryClient;
}) => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider theme={createAppTheme()}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  </QueryClientProvider>
);

export const renderWithProviders = (
  ui: ReactElement,
  options: RenderOptions & ProvidersOptions = {},
) => {
  const queryClient =
    options.queryClient ?? createTestQueryClient();

  const result = render(ui, {
    ...options,
    wrapper: ({ children }) => (
      <Providers queryClient={queryClient}>
        {children}
      </Providers>
    ),
  });

  return { ...result, queryClient };
};

export const renderHookWithProviders = <Result, Props>(
  callback: (props: Props) => Result,
  options: RenderHookOptions<Props> & ProvidersOptions = {},
) => {
  const queryClient =
    options.queryClient ?? createTestQueryClient();

  const result = renderHook(callback, {
    ...options,
    wrapper: ({ children }) => (
      <Providers queryClient={queryClient}>
        {children}
      </Providers>
    ),
  });

  return { ...result, queryClient };
};

