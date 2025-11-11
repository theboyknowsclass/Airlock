import axios, {
  AxiosError,
  AxiosResponse,
  isAxiosError,
} from 'axios';

const VERSION_ENDPOINT = '/api/version';
const DEFAULT_TIMEOUT_MS = 1_000;

type HeaderValue = string | string[] | undefined;

export interface ServerVersion {
  version: string;
  displayLabel: string;
  retrievedAt: string;
  buildTimestamp?: string;
  source?: string;
}

export type ServerVersionRequestErrorType =
  | 'timeout'
  | 'network'
  | 'server'
  | 'unknown';

export class ServerVersionRequestError extends Error {
  public readonly type: ServerVersionRequestErrorType;

  public readonly status?: number;

  public readonly requestId?: string;

  public readonly clientRequestId: string;

  public override readonly cause?: unknown;

  constructor(
    type: ServerVersionRequestErrorType,
    message: string,
    options: {
      status?: number;
      requestId?: string;
      clientRequestId: string;
      cause?: unknown;
    },
  ) {
    super(message, { cause: options.cause });
    this.name = 'ServerVersionRequestError';
    this.type = type;
    this.status = options.status;
    this.requestId = options.requestId;
    this.clientRequestId = options.clientRequestId;
    this.cause = options.cause;
  }
}

export const isServerVersionRequestError = (
  error: unknown,
): error is ServerVersionRequestError =>
  error instanceof ServerVersionRequestError;

export interface ServerVersionFetchResult {
  data: ServerVersion;
  clientRequestId: string;
  requestId?: string;
}

const httpClient = axios.create({
  headers: {
    Accept: 'application/json',
  },
});

const toHeaderValue = (value: HeaderValue) =>
  Array.isArray(value) ? value[0] : value;

const extractRequestId = (
  response: AxiosResponse | undefined,
  fallback: string,
): string | undefined => {
  if (!response) {
    return fallback;
  }

  const headers = response.headers ?? {};
  const requestIdHeader =
    toHeaderValue(
      (headers as Record<string, HeaderValue>)['x-request-id'],
    ) ??
    toHeaderValue(
      (headers as Record<string, HeaderValue>)['X-Request-Id'],
    );

  return requestIdHeader ?? fallback;
};

export interface FetchServerVersionOptions {
  signal?: AbortSignal;
  timeoutMs?: number;
}

export async function fetchServerVersion({
  signal,
  timeoutMs = DEFAULT_TIMEOUT_MS,
}: FetchServerVersionOptions = {}): Promise<ServerVersionFetchResult> {
  const clientRequestId =
    typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
      ? crypto.randomUUID()
      : Math.random().toString(36).slice(2);

  let didTimeout = false;

  const controller = new AbortController();

  const abortWithReason = (reason?: unknown) => {
    if (!controller.signal.aborted) {
      controller.abort(reason);
    }
  };

  const timeoutHandle = setTimeout(() => {
    didTimeout = true;
    abortWithReason(
      new DOMException(
        'Server version request exceeded one second timeout.',
        'TimeoutError',
      ),
    );
  }, timeoutMs);

  if (signal) {
    if (signal.aborted) {
      abortWithReason(signal.reason);
    } else {
      signal.addEventListener(
        'abort',
        () => {
          abortWithReason(signal.reason);
        },
        { once: true },
      );
    }
  }

  try {
    const response = await httpClient.get<ServerVersion>(VERSION_ENDPOINT, {
      signal: controller.signal,
      headers: {
        'x-request-id': clientRequestId,
        'x-client-request-id': clientRequestId,
      },
    });

    return {
      data: response.data,
      clientRequestId,
      requestId: extractRequestId(response, clientRequestId),
    };
  } catch (unknownError: unknown) {
    if (
      !didTimeout &&
      (unknownError instanceof DOMException &&
        unknownError.name === 'AbortError')
    ) {
      throw unknownError;
    }

    if (
      !didTimeout &&
      isAxiosError(unknownError) &&
      unknownError.code === AxiosError.ERR_CANCELED
    ) {
      throw new DOMException('Server version request cancelled.', 'AbortError');
    }

    if (isAxiosError(unknownError)) {
      const status = unknownError.response?.status;
      const requestId = extractRequestId(
        unknownError.response,
        clientRequestId,
      );

      if (didTimeout || unknownError.code === AxiosError.ERR_CANCELED) {
        throw new ServerVersionRequestError(
          'timeout',
          'Server version request timed out after one second.',
          {
            status,
            requestId,
            clientRequestId,
            cause: unknownError,
          },
        );
      }

      if (unknownError.code === AxiosError.ERR_NETWORK) {
        throw new ServerVersionRequestError(
          'network',
          'Network error while requesting server version.',
          {
            status,
            requestId,
            clientRequestId,
            cause: unknownError,
          },
        );
      }

      if (typeof status === 'number') {
        const serverMessage =
          typeof unknownError.response?.data === 'object' &&
          unknownError.response?.data !== null &&
          'message' in
            (unknownError.response?.data as Record<string, unknown>)
            ? String(
                (
                  unknownError.response?.data as Record<string, unknown>
                ).message,
              )
            : `Server responded with status ${status}.`;

        throw new ServerVersionRequestError(
          'server',
          serverMessage,
          {
            status,
            requestId,
            clientRequestId,
            cause: unknownError,
          },
        );
      }
    }

    throw new ServerVersionRequestError(
      didTimeout ? 'timeout' : 'unknown',
      didTimeout
        ? 'Server version request timed out after one second.'
        : 'Unexpected error requesting server version.',
      {
        requestId: clientRequestId,
        clientRequestId,
        cause: unknownError,
      },
    );
  } finally {
    clearTimeout(timeoutHandle);
  }
}

