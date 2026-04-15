export type ApiSuccessResponse<T> = {
  success: true;
  data: T;
};

export type ApiErrorPayload = {
  code: string;
  message: string;
  details?: unknown;
};

export type ApiErrorResponse = {
  success: false;
  error: ApiErrorPayload;
};

export type AuthUser = {
  id: number;
  username: string;
  createdAt: string;
  updatedAt: string;
};

export type LinkCategory = string;

export type LinkCategoryEntry = {
  slug: LinkCategory;
  label: string;
};

export type LinkStatus = "working" | "down" | "unknown" | "seized";

export type LinkItem = {
  id: number;
  link: string;
  title: string;
  description: string;
  categories: LinkCategoryEntry[];
  status: LinkStatus;
  addedById: number;
  createdAt: string;
  updatedAt: string;
  isInReadLater: boolean;
  addedBy: {
    id: number;
    username: string;
  };
};

export type LinkFormValues = {
  title: string;
  link: string;
  description: string;
  categories: LinkCategory[];
  status: LinkStatus;
};

export type PaginatedLinksResponse = {
  items: LinkItem[];
  meta: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
};
