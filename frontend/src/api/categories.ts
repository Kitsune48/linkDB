import { apiClient } from "./client";
import type { LinkCategoryEntry } from "./types";

export const categoriesApi = {
  list() {
    return apiClient.get<LinkCategoryEntry[]>("/api/categories");
  },
};
