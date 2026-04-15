import { apiClient } from "./client";
import type {
  LinkCategory,
  LinkFormValues,
  LinkItem,
  LinkStatus,
  PaginatedLinksResponse,
} from "./types";

export type ListLinksParams = {
  q?: string;
  categories?: LinkCategory[];
  status?: LinkStatus | "";
  addedBy?: number;
  page?: number;
  limit?: number;
};

function buildLinksQuery(params: ListLinksParams) {
  const searchParams = new URLSearchParams();

  if (params.q) {
    searchParams.set("q", params.q);
  }

  if (params.categories?.length) {
    params.categories.forEach((category) => {
      searchParams.append("categories", category);
    });
  }

  if (params.status) {
    searchParams.set("status", params.status);
  }

  if (params.addedBy) {
    searchParams.set("addedBy", String(params.addedBy));
  }

  if (params.page) {
    searchParams.set("page", String(params.page));
  }

  if (params.limit) {
    searchParams.set("limit", String(params.limit));
  }

  const queryString = searchParams.toString();
  return queryString ? `/api/links?${queryString}` : "/api/links";
}

export const linksApi = {
  list(params: ListLinksParams) {
    return apiClient.get<PaginatedLinksResponse>(buildLinksQuery(params));
  },
  create(input: LinkFormValues) {
    return apiClient.post<LinkItem>("/api/links", input);
  },
  update(id: number, input: Partial<LinkFormValues>) {
    return apiClient.patch<LinkItem>(`/api/links/${id}`, input);
  },
  remove(id: number) {
    return apiClient.delete<{ message: string }>(`/api/links/${id}`);
  },
};
