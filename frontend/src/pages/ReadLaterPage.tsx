import { useEffect, useState } from "react";

import { ApiClientError } from "../api/client";
import { readLaterApi } from "../api/read-later";
import type { LinkItem } from "../api/types";
import { LinkCard } from "../components/links/LinkCard";

export function ReadLaterPage() {
  const [items, setItems] = useState<LinkItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);
  const [submittingId, setSubmittingId] = useState<number | null>(null);

  async function loadReadLater() {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const response = await readLaterApi.list();
      setItems(response);
    } catch (error) {
      setItems([]);
      setErrorMessage(
        error instanceof ApiClientError ? error.message : "Failed to load read later links.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadReadLater();
  }, []);

  async function handleRemove(item: LinkItem) {
    setSubmittingId(item.id);
    setFeedbackMessage(null);

    try {
      await readLaterApi.remove(item.id);
      await loadReadLater();
      setFeedbackMessage("Removed from read later.");
    } catch (error) {
      setErrorMessage(
        error instanceof ApiClientError ? error.message : "Failed to update read later.",
      );
    } finally {
      setSubmittingId(null);
    }
  }

  return (
    <section className="space-y-6">
      <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20 sm:p-7">
        <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
          Personal queue
        </span>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight text-slate-100 sm:text-3xl">
          Read Later
        </h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
          Your personal list of links to read or watch later.
        </p>
      </div>

      {feedbackMessage ? (
        <p className="rounded-2xl border border-emerald-900/70 bg-emerald-950/30 px-4 py-3 text-sm text-emerald-200">
          {feedbackMessage}
        </p>
      ) : null}

      {isLoading ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-8 text-center text-sm text-slate-300">
          Loading read later links...
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
          <h2 className="text-lg font-semibold text-slate-100">Read later is empty</h2>
          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-400">
            Use the add button from search results to build your personal queue.
          </p>
        </div>
      ) : null}

      {!isLoading && !errorMessage && items.length > 0 ? (
        <div className="space-y-4">
          {items.map((item) => (
            <LinkCard
              key={item.id}
              item={item}
              isReadLaterSubmitting={submittingId === item.id}
              readLaterButtonLabel="Remove From Read Later"
              onToggleReadLater={() => void handleRemove(item)}
            />
          ))}
        </div>
      ) : null}
    </section>
  );
}
