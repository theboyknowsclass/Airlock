import { useMemo, useRef } from 'react';
import {
  useQuery,
  type UseQueryOptions,
  type UseQueryResult,
} from '@tanstack/react-query';

import {
  fetchServerVersion,
  type FetchServerVersionOptions,
  type ServerVersion,
  type ServerVersionFetchResult,
  ServerVersionRequestError,
  isServerVersionRequestError,
} from '../services/versionService';

export const SERVER_VERSION_QUERY_KEY = ['serverVersion'] as const;

export type UseServerVersionOptions = Omit<
  UseQueryOptions<
    ServerVersionFetchResult,
    ServerVersionRequestError,
    ServerVersion
  >,
  'queryKey' | 'queryFn' | 'select'
> &
  Pick<FetchServerVersionOptions, 'timeoutMs'>;

export type UseServerVersionResult = UseQueryResult<
  ServerVersion,
  ServerVersionRequestError
> & {
  clientRequestId?: string;
  requestId?: string;
  isTimeoutError: boolean;
  isNetworkError: boolean;
  isServerError: boolean;
};

export function useServerVersion(
  options?: UseServerVersionOptions,
): UseServerVersionResult {
  const lastClientRequestIdRef = useRef<string>();
  const lastRequestIdRef = useRef<string>();

  const {
    timeoutMs,
    ...queryOptions
  } = options ?? {};

  const query = useQuery<
    ServerVersionFetchResult,
    ServerVersionRequestError,
    ServerVersion
  >({
    queryKey: SERVER_VERSION_QUERY_KEY,
    queryFn: async ({ signal }) => {
      try {
        const result = await fetchServerVersion({
          signal,
          timeoutMs,
        });
        lastClientRequestIdRef.current = result.clientRequestId;
        lastRequestIdRef.current =
          result.requestId ?? result.clientRequestId;
        return result;
      } catch (error) {
        if (isServerVersionRequestError(error)) {
          lastClientRequestIdRef.current = error.clientRequestId;
          lastRequestIdRef.current =
            error.requestId ?? error.clientRequestId;
        }
        throw error;
      }
    },
    select: (result) => result.data,
    retry: false,
    ...queryOptions,
  });

  const clientRequestId = lastClientRequestIdRef.current;
  const requestId = lastRequestIdRef.current;

  const { error } = query;

  const isTimeoutError =
    !!error && error.type === 'timeout';
  const isNetworkError =
    !!error && error.type === 'network';
  const isServerError =
    !!error && error.type === 'server';

  return useMemo(
    () => ({
      ...query,
      clientRequestId,
      requestId,
      isTimeoutError,
      isNetworkError,
      isServerError,
    }),
    [
      query,
      clientRequestId,
      requestId,
      isTimeoutError,
      isNetworkError,
      isServerError,
    ],
  );
}

