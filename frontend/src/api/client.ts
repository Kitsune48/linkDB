import type { ApiErrorPayload, ApiErrorResponse, ApiSuccessResponse } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:3000";

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
};

export class ApiClientError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly details?: unknown,
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

async function request<T>(path: string, options: RequestOptions = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  });

  const payload = (await response.json()) as ApiSuccessResponse<T> | ApiErrorResponse;

  if (!response.ok || !payload.success) {
    const error = (payload as ApiErrorResponse).error;
    throw new ApiClientError(
      response.status,
      error?.code ?? "UNKNOWN_ERROR",
      error?.message ?? "Unexpected API error.",
      error?.details,
    );
  }

  return payload.data;
}

export const apiClient = {
  get<T>(path: string) {
    return request<T>(path, { method: "GET" });
  },
  post<T>(path: string, body?: unknown) {
    return request<T>(path, { method: "POST", body });
  },
  patch<T>(path: string, body?: unknown) {
    return request<T>(path, { method: "PATCH", body });
  },
  delete<T>(path: string) {
    return request<T>(path, { method: "DELETE" });
  },
};

export function isUnauthenticatedError(error: unknown) {
  return error instanceof ApiClientError && error.status === 401;
}

export type { ApiErrorPayload };
