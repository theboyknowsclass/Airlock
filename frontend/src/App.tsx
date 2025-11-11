import { useMemo, useRef } from 'react';
import { CssBaseline, ThemeProvider } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { createAppTheme } from './theme';
import { InitialSite } from './pages/InitialSite';

const createQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        staleTime: 0,
        refetchOnWindowFocus: false,
      },
    },
  });

export function App() {
  const queryClientRef = useRef<QueryClient>();
  if (!queryClientRef.current) {
    queryClientRef.current = createQueryClient();
  }

  const theme = useMemo(() => createAppTheme(), []);

  return (
    <QueryClientProvider client={queryClientRef.current}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <InitialSite />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;

