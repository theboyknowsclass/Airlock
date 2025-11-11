import { afterEach, describe, expect, it, vi } from 'vitest';
import { InitialSite } from './InitialSite';
import { renderWithProviders } from '../test-utils/renderWithProviders';
import { ServerVersionRequestError } from '../services/versionService';
import { useServerVersion } from '../hooks/useServerVersion';
import type { UseServerVersionResult } from '../hooks/useServerVersion';

vi.mock('../hooks/useServerVersion', () => ({
  useServerVersion: vi.fn(),
}));

const mockedUseServerVersion = vi.mocked(useServerVersion);

const createQueryResult = (
  overrides: Partial<UseServerVersionResult>,
): UseServerVersionResult => {
  const base = {
    data: undefined,
    error: null,
    status: 'pending',
    fetchStatus: 'idle',
    isError: false,
    isPending: true,
    isLoading: true,
    isSuccess: false,
    isFetching: false,
    isFetched: false,
    isFetchedAfterMount: false,
    isInitialLoading: true,
    isLoadingError: false,
    isPlaceholderData: false,
    isRefetchError: false,
    isRefetching: false,
    isStale: true,
    isPaused: false,
    dataUpdatedAt: 0,
    errorUpdatedAt: 0,
    errorUpdateCount: 0,
    failureCount: 0,
    failureReason: null,
    refetch: vi.fn(),
    clientRequestId: undefined,
    requestId: undefined,
    isTimeoutError: false,
    isNetworkError: false,
    isServerError: false,
  };

  return { ...base, ...overrides } as unknown as UseServerVersionResult;
};

describe('InitialSite', () => {
  afterEach(() => {
    mockedUseServerVersion.mockReset();
  });

  it('renders the placeholder while awaiting server version data', () => {
    mockedUseServerVersion.mockReturnValue(createQueryResult({}));

    const { getByRole } = renderWithProviders(<InitialSite />);

    expect(getByRole('status')).toHaveAccessibleName(
      /loading server version/i,
    );
  });

  it('renders the version badge once data is available', () => {
    mockedUseServerVersion.mockReturnValue(
      createQueryResult({
        data: {
          version: '1.2.3',
          displayLabel: 'v1.2.3',
          retrievedAt: '2025-11-11T12:00:00.000Z',
          source: 'api',
        },
        status: 'success',
        isSuccess: true,
        isPending: false,
        isFetched: true,
        clientRequestId: 'client-abc',
        requestId: 'server-abc',
      }),
    );

    const { getByRole, queryByRole } = renderWithProviders(
      <InitialSite />,
    );

    const status = getByRole('status');
    expect(status).toHaveAccessibleName(/server version/i);
    expect(
      queryByRole('status', { name: /loading/i }),
    ).not.toBeInTheDocument();
  });

  it('transitions to the error view and retries on request failure', async () => {
    const refetch = vi.fn();
    const error = new ServerVersionRequestError(
      'timeout',
      'Request timed out.',
      {
        clientRequestId: 'client-def',
        requestId: 'server-def',
      },
    );

    mockedUseServerVersion.mockReturnValue(
      createQueryResult({
        status: 'error',
        isError: true,
        isPending: false,
        isSuccess: false,
        error,
        refetch,
        isTimeoutError: true,
      }),
    );

    const { getByRole, getByText } = renderWithProviders(
      <InitialSite />,
    );

    expect(
      getByRole('heading', { name: /cannot load/i }),
    ).toBeInTheDocument();

    getByText(/try again/i).click();

    expect(refetch).toHaveBeenCalledWith(
      expect.objectContaining({ cancelRefetch: false }),
    );
  });
});

