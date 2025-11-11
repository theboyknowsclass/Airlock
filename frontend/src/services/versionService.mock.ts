import { http, HttpResponse, delay } from 'msw';

import type { ServerVersion } from './versionService';

const VERSION_ENDPOINT = '/api/version';

const baseVersion: ServerVersion = {
  version: '1.2.3',
  displayLabel: 'v1.2.3',
  retrievedAt: new Date().toISOString(),
  source: 'api',
  buildTimestamp: new Date().toISOString(),
};

export interface ServerVersionSuccessOptions {
  delayMs?: number;
}

export const createServerVersionSuccessHandler = (
  overrides?: Partial<ServerVersion>,
  options?: ServerVersionSuccessOptions,
) =>
  http.get(VERSION_ENDPOINT, async () => {
    if (options?.delayMs) {
      await delay(options.delayMs);
    }

    return HttpResponse.json({
      ...baseVersion,
      ...overrides,
    });
  });

export const createServerVersionPendingHandler = () =>
  http.get(VERSION_ENDPOINT, async () => {
    await delay('infinite');
    return HttpResponse.json(baseVersion);
  });

export interface ServerVersionErrorOptions {
  status?: number;
  error?: string;
  message?: string;
  delayMs?: number;
}

export const createServerVersionErrorHandler = (
  options?: ServerVersionErrorOptions,
) =>
  http.get(VERSION_ENDPOINT, async () => {
    if (options?.delayMs) {
      await delay(options.delayMs);
    }

    return HttpResponse.json(
      {
        error: options?.error ?? 'version_unavailable',
        message:
          options?.message ??
          'Failed to retrieve the server version. Please try again.',
      },
      {
        status: options?.status ?? 503,
      },
    );
  });

export const defaultServerVersionHandlers = [
  createServerVersionSuccessHandler(),
];


