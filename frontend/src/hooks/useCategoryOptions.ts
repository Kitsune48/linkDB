import { useEffect, useState } from "react";

import { categoriesApi } from "../api/categories";
import type { LinkCategoryEntry } from "../api/types";

export function useCategoryOptions() {
  const [categoryOptions, setCategoryOptions] = useState<LinkCategoryEntry[]>([]);

  useEffect(() => {
    async function loadCategories() {
      try {
        const response = await categoriesApi.list();
        setCategoryOptions(response);
      } catch (error) {
        console.error(error);
      }
    }

    void loadCategories();
  }, []);

  return categoryOptions;
}
