import { useState } from "react";

import { ApiClientError } from "../api/client";
import { linksApi } from "../api/links";
import type { LinkFormValues } from "../api/types";
import { LinkForm } from "../components/links/LinkForm";
import { useCategoryOptions } from "../hooks/useCategoryOptions";

export function NewLinkPage() {
  const categoryOptions = useCategoryOptions();
  const [createError, setCreateError] = useState<string | null>(null);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [createResetKey, setCreateResetKey] = useState(0);

  async function handleCreate(values: LinkFormValues) {
    setCreateError(null);
    setFeedbackMessage(null);
    setIsCreating(true);

    try {
      await linksApi.create(values);
      setCreateResetKey((current) => current + 1);
      setFeedbackMessage("Link created successfully.");
    } catch (error) {
      setCreateError(
        error instanceof ApiClientError ? error.message : "Failed to create link.",
      );
    } finally {
      setIsCreating(false);
    }
  }

  return (
    <section className="space-y-6">
      <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20 sm:p-7">
        <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
          Save something new
        </span>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight text-slate-100 sm:text-3xl">
          New Link
        </h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
          Add a new link to the shared collection without the clutter of filters and search results.
        </p>
      </div>

      {feedbackMessage ? (
        <p className="rounded-2xl border border-emerald-900/70 bg-emerald-950/30 px-4 py-3 text-sm text-emerald-200">
          {feedbackMessage}
        </p>
      ) : null}

      <LinkForm
        categoryOptions={categoryOptions}
        resetKey={createResetKey}
        submitLabel="Create link"
        isSubmitting={isCreating}
        serverError={createError}
        onSubmit={handleCreate}
      />
    </section>
  );
}
