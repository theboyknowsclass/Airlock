import axe from 'axe-core';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { InitialSite } from '../../src/pages/InitialSite';
import { renderWithProviders } from '../../src/test-utils/renderWithProviders';
import {
  ServerVersionRequestError,
  type ServerVersion,
} from '../../src/services/versionService';
import {
  useServerVersion,
  type UseServerVersionResult,
} from '../../src/hooks/useServerVersion';

vi.mock('../../src/hooks/useServerVersion', () => ({
  useServerVersion: vi.fn(),
}));

const mockedUseServerVersion = vi.mocked(useServerVersion);

const createResult = (
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

const renderAndAudit = async () => {
  const { container } = renderWithProviders(<InitialSite />);
  const results = await axe.run(container, {
    rules: {
      'color-contrast': { enabled: false },
    },
  });
  expect(results.violations).toHaveLength(0);
};

describe('InitialSite accessibility', () => {
  afterEach(() => {
    mockedUseServerVersion.mockReset();
  });

  it('contains no axe violations in the success state', async () => {
    const version: ServerVersion = {
      version: '1.2.3',
      displayLabel: 'v1.2.3',
      retrievedAt: new Date().toISOString(),
      source: 'api',
    };

    mockedUseServerVersion.mockReturnValue(
      createResult({
        data: version,
        status: 'success',
        isSuccess: true,
        isPending: false,
        isFetched: true,
      }),
    );

    await renderAndAudit();
  });

  it('contains no axe violations in the error state', async () => {
    const error = new ServerVersionRequestError(
      'timeout',
      'Request timed out.',
      {
        clientRequestId: 'client-xyz',
        requestId: 'req-xyz',
      },
    );

    mockedUseServerVersion.mockReturnValue(
      createResult({
        status: 'error',
        isError: true,
        isPending: false,
        isSuccess: false,
        error,
        isTimeoutError: true,
      }),
    );

    await renderAndAudit();
  });
});

