import { waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  renderHookWithProviders,
  createTestQueryClient,
} from '../test-utils/renderWithProviders';
import { useServerVersion } from './useServerVersion';
import type { ServerVersionFetchResult } from '../services/versionService';
import {
  ServerVersionRequestError,
  fetchServerVersion,
} from '../services/versionService';

vi.mock('../services/versionService', async () => {
  const actual =
    await vi.importActual<typeof import('../services/versionService')>(
      '../services/versionService',
    );
  return {
    ...actual,
    fetchServerVersion: vi.fn(actual.fetchServerVersion),
  };
});

const mockedFetchServerVersion = vi.mocked(fetchServerVersion);

describe('useServerVersion', () => {
  afterEach(() => {
    mockedFetchServerVersion.mockReset();
  });

  it('returns server version data when the request succeeds', async () => {
    const response: ServerVersionFetchResult = {
      data: {
        version: '1.2.3',
        displayLabel: 'v1.2.3',
        retrievedAt: new Date().toISOString(),
        source: 'api',
      },
      clientRequestId: 'client-123',
      requestId: 'req-123',
    };
    mockedFetchServerVersion.mockResolvedValue(response);

    const queryClient = createTestQueryClient();
    const { result } = renderHookWithProviders(useServerVersion, {
      queryClient,
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(response.data);
    expect(result.current.clientRequestId).toBe('client-123');
    expect(result.current.requestId).toBe('req-123');
  });

  it('exposes timeout error metadata when the request exceeds one second', async () => {
    const error = new ServerVersionRequestError(
      'timeout',
      'Request timed out.',
      {
        clientRequestId: 'client-456',
        requestId: 'req-456',
      },
    );
    mockedFetchServerVersion.mockRejectedValue(error);

    const queryClient = createTestQueryClient();
    const { result } = renderHookWithProviders(useServerVersion, {
      queryClient,
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.isTimeoutError).toBe(true);
    expect(result.current.error).toBe(error);
    expect(result.current.clientRequestId).toBe('client-456');
    expect(result.current.requestId).toBe('req-456');
  });
});

