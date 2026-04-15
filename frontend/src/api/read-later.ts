import { apiClient } from "./client";
import type { LinkItem } from "./types";

export const readLaterApi = {
  list() {
    return apiClient.get<LinkItem[]>("/api/read-later");
  },
  add(linkId: number) {
    return apiClient.post<LinkItem>(`/api/read-later/${linkId}`);
  },
  remove(linkId: number) {
    return apiClient.delete<{ message: string }>(`/api/read-later/${linkId}`);
  },
};
