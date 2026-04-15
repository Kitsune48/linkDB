import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { ApiClientError } from "../api/client";
import { linksApi } from "../api/links";
import { readLaterApi } from "../api/read-later";
import type { LinkCategory, LinkFormValues, LinkItem, LinkStatus } from "../api/types";
import { LinkCard } from "../components/links/LinkCard";
import { LinkForm } from "../components/links/LinkForm";
import { LinksFilters } from "../components/links/LinksFilters";
import { Pagination } from "../components/links/Pagination";
import { useAuth } from "../hooks/useAuth";
import { useCategoryOptions } from "../hooks/useCategoryOptions";

const PAGE_LIMIT = 10;

type LinksMeta = {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
};

function parsePositiveNumber(value: string | null, fallback: number) {
  const parsed = Number(value);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : fallback;
}

export function SearchLinksPage() {
  const { user } = useAuth();
  const categoryOptions = useCategoryOptions();
  const [searchParams, setSearchParams] = useSearchParams();
  const [items, setItems] = useState<LinkItem[]>([]);
  const [meta, setMeta] = useState<LinksMeta>({
    page: 1,
    limit: PAGE_LIMIT,
    total: 0,
    totalPages: 1,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editError, setEditError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [readLaterSubmittingId, setReadLaterSubmittingId] = useState<number | null>(null);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);

  const query = searchParams.get("q") ?? "";
  const categoryParams = searchParams.getAll("categories");
  const legacyCategory = searchParams.get("category");
  const categories =
    categoryParams.length > 0
      ? (categoryParams.filter(Boolean) as LinkCategory[])
      : legacyCategory
        ? [legacyCategory as LinkCategory]
        : [];
  const categoriesKey = categories.join("|");
  const status = (searchParams.get("status") ?? "") as LinkStatus | "";
  const addedByMe = searchParams.get("addedBy") === "me";
  const page = parsePositiveNumber(searchParams.get("page"), 1);
  const editingItem = items.find((item) => item.id === editingId) ?? null;

  async function loadLinks() {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const response = await linksApi.list({
        q: query || undefined,
        categories,
        status,
        addedBy: addedByMe && user ? user.id : undefined,
        page,
        limit: PAGE_LIMIT,
      });

      setItems(response.items);
      setMeta(response.meta);
    } catch (error) {
      setItems([]);
      setMeta({
        page: 1,
        limit: PAGE_LIMIT,
        total: 0,
        totalPages: 1,
      });
      setErrorMessage(
        error instanceof ApiClientError
          ? error.message
          : "Failed to load links.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadLinks();
  }, [addedByMe, categoriesKey, page, query, status, user]);

  function updateParams(next: {
    q?: string;
    categories?: LinkCategory[];
    status?: LinkStatus | "";
    addedByMe?: boolean;
    page?: number;
  }) {
    const params = new URLSearchParams(searchParams);

    if (next.q !== undefined) {
      next.q ? params.set("q", next.q) : params.delete("q");
    }

    if (next.categories !== undefined) {
      params.delete("categories");
      params.delete("category");
      next.categories.forEach((category) => {
        params.append("categories", category);
      });
    }

    if (next.status !== undefined) {
      next.status ? params.set("status", next.status) : params.delete("status");
    }

    if (next.addedByMe !== undefined) {
      next.addedByMe ? params.set("addedBy", "me") : params.delete("addedBy");
    }

    if (next.page !== undefined) {
      next.page > 1 ? params.set("page", String(next.page)) : params.delete("page");
    }

    setSearchParams(params);
  }

  async function handleUpdate(values: LinkFormValues) {
    if (!editingId) {
      return;
    }

    setEditError(null);
    setFeedbackMessage(null);
    setIsEditing(true);

    try {
      await linksApi.update(editingId, values);
      await loadLinks();
      setFeedbackMessage("Link updated successfully.");
      setEditingId(null);
    } catch (error) {
      setEditError(
        error instanceof ApiClientError ? error.message : "Failed to update link.",
      );
    } finally {
      setIsEditing(false);
    }
  }

  async function handleDelete(item: LinkItem) {
    const confirmed = window.confirm(`Delete "${item.title}"?`);
    if (!confirmed) {
      return;
    }

    setDeletingId(item.id);
    setFeedbackMessage(null);
    setErrorMessage(null);

    try {
      await linksApi.remove(item.id);
      if (editingId === item.id) {
        setEditingId(null);
      }
      await loadLinks();
      setFeedbackMessage("Link deleted successfully.");
    } catch (error) {
      setErrorMessage(
        error instanceof ApiClientError ? error.message : "Failed to delete link.",
      );
    } finally {
      setDeletingId(null);
    }
  }

  async function handleToggleReadLater(item: LinkItem) {
    setReadLaterSubmittingId(item.id);
    setFeedbackMessage(null);

    try {
      if (item.isInReadLater) {
        await readLaterApi.remove(item.id);
        setFeedbackMessage("Removed from read later.");
      } else {
        await readLaterApi.add(item.id);
        setFeedbackMessage("Added to read later.");
      }
      await loadLinks();
    } catch (error) {
      setErrorMessage(
        error instanceof ApiClientError ? error.message : "Failed to update read later.",
      );
    } finally {
      setReadLaterSubmittingId(null);
    }
  }

  return (
    <section className="space-y-6">
      <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20 sm:p-7">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div className="space-y-2">
            <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
              Explore collection
            </span>
            <h1 className="text-2xl font-semibold tracking-tight text-slate-100 sm:text-3xl">
              Search Links
            </h1>
            <p className="max-w-2xl text-sm leading-6 text-slate-400">
              Search, filter, save to read later, and manage your saved links.
            </p>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm text-slate-400">
            <span className="block text-[11px] uppercase tracking-[0.18em] text-slate-500">
              Total links
            </span>
            <span className="mt-1 block text-2xl font-semibold text-slate-100">
              {meta.total}
            </span>
          </div>
        </div>
      </div>

      {feedbackMessage ? (
        <p className="rounded-2xl border border-emerald-900/70 bg-emerald-950/30 px-4 py-3 text-sm text-emerald-200">
          {feedbackMessage}
        </p>
      ) : null}

      <LinksFilters
        initialQuery={query}
        initialCategories={categories}
        initialStatus={status}
        initialAddedByMe={addedByMe}
        categoryOptions={categoryOptions}
        onApply={(filters) =>
          updateParams({
            q: filters.q,
            categories: filters.categories,
            status: filters.status,
            addedByMe: filters.addedByMe,
            page: 1,
          })
        }
      />

      <div className="flex flex-col gap-2 text-sm text-slate-400 sm:flex-row sm:items-center sm:justify-between">
        <span>
          {meta.total} result{meta.total === 1 ? "" : "s"}
        </span>
        <span>Showing {items.length} on this page</span>
      </div>

      {isLoading ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-8 text-center text-sm text-slate-300">
          <div className="mx-auto mb-3 h-10 w-10 animate-pulse rounded-full border border-slate-700 bg-slate-800" />
          Loading links...
        </div>
      ) : null}

      {!isLoading && errorMessage ? (
        <div className="rounded-3xl border border-red-900/70 bg-red-950/40 p-6 text-sm text-red-200">
          <h2 className="text-base font-semibold text-red-100">Something went wrong</h2>
          <p className="mt-2 leading-6">{errorMessage}</p>
        </div>
      ) : null}

      {!isLoading && !errorMessage && items.length === 0 ? (
        <div className="rounded-3xl border border-dashed border-slate-700 bg-slate-900/70 p-8 text-center">
          <h2 className="text-lg font-semibold text-slate-100">No links found</h2>
          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-400">
            Try changing the search terms or clearing filters to see more results.
          </p>
        </div>
      ) : null}

      {!isLoading && !errorMessage && items.length > 0 ? (
        <div className="space-y-4">
          {items.map((item) => (
            <div key={item.id} className="space-y-3">
              <LinkCard
                item={item}
                isOwner={user?.id === item.addedBy.id}
                isDeleting={deletingId === item.id}
                isReadLaterSubmitting={readLaterSubmittingId === item.id}
                onToggleReadLater={() => void handleToggleReadLater(item)}
                onEdit={() => {
                  setEditingId(item.id);
                  setEditError(null);
                  setFeedbackMessage(null);
                }}
                onDelete={() => void handleDelete(item)}
              />
              {editingItem?.id === item.id ? (
                <LinkForm
                  categoryOptions={categoryOptions}
                  initialValues={{
                    title: item.title,
                    link: item.link,
                    description: item.description,
                    categories: item.categories.map((category) => category.slug),
                    status: item.status,
                  }}
                  submitLabel="Save changes"
                  isSubmitting={isEditing}
                  serverError={editError}
                  onCancel={() => {
                    setEditingId(null);
                    setEditError(null);
                  }}
                  onSubmit={handleUpdate}
                />
              ) : null}
            </div>
          ))}
        </div>
      ) : null}

      {!isLoading && !errorMessage && meta.totalPages > 1 ? (
        <Pagination
          page={meta.page}
          totalPages={meta.totalPages}
          onChange={(nextPage) => updateParams({ page: nextPage })}
        />
      ) : null}
    </section>
  );
}
