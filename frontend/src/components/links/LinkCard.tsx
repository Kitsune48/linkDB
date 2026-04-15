import type { LinkItem } from "../../api/types";
import { Badge } from "../ui/Badge";

type LinkCardProps = {
  item: LinkItem;
  isOwner?: boolean;
  isDeleting?: boolean;
  isReadLaterSubmitting?: boolean;
  readLaterButtonLabel?: string;
  onEdit?: () => void;
  onDelete?: () => void;
  onToggleReadLater?: () => void;
};

function formatDate(value: string) {
  return new Intl.DateTimeFormat("it-IT", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function LinkCard({
  item,
  isOwner = false,
  isDeleting = false,
  isReadLaterSubmitting = false,
  readLaterButtonLabel,
  onEdit,
  onDelete,
  onToggleReadLater,
}: LinkCardProps) {
  return (
    <article className="rounded-3xl border border-slate-800 bg-slate-900/90 p-5 shadow-lg shadow-slate-950/20 transition hover:border-slate-700 sm:p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            {item.categories.map((category) => (
              <Badge key={category.slug} tone={category.slug}>
                {category.label}
              </Badge>
            ))}
            <Badge tone={item.status}>{item.status[0].toUpperCase() + item.status.slice(1)}</Badge>
          </div>
          <h2 className="mt-3 text-lg font-semibold leading-tight text-slate-100 sm:text-xl">
            {item.title}
          </h2>
          <a
            href={item.link}
            target="_blank"
            rel="noreferrer"
            className="mt-2 inline-block break-all text-sm text-brand-100 underline decoration-slate-600 underline-offset-4 transition hover:text-white"
          >
            {item.link}
          </a>
        </div>
        <div className="flex flex-wrap gap-2 lg:justify-end">
          {onToggleReadLater ? (
            <button
              type="button"
              onClick={onToggleReadLater}
              disabled={isReadLaterSubmitting}
              className="rounded-lg border border-brand-700/70 px-3 py-2 text-sm text-brand-100 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {isReadLaterSubmitting
                ? "Saving..."
                : (readLaterButtonLabel ?? (item.isInReadLater ? "Remove From Read Later" : "Add To Read Later"))}
            </button>
          ) : null}
          {isOwner ? (
            <>
              <button
                type="button"
                onClick={onEdit}
                className="rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-200 transition hover:bg-slate-800"
              >
                Edit
              </button>
              <button
                type="button"
                onClick={onDelete}
                disabled={isDeleting}
                className="rounded-lg border border-red-900/70 px-3 py-2 text-sm text-red-200 transition hover:bg-red-950/40 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {isDeleting ? "Deleting..." : "Delete"}
              </button>
            </>
          ) : null}
        </div>
      </div>

      <p className="mt-4 text-sm leading-6 text-slate-300">{item.description}</p>

      <dl className="mt-5 grid gap-4 rounded-2xl border border-slate-800 bg-slate-950/60 p-4 text-sm text-slate-400 sm:grid-cols-3">
        <div className="min-w-0">
          <dt className="text-[11px] uppercase tracking-[0.18em] text-slate-500">Author</dt>
          <dd className="mt-1 truncate text-slate-200">{item.addedBy.username}</dd>
        </div>
        <div>
          <dt className="text-[11px] uppercase tracking-[0.18em] text-slate-500">Created</dt>
          <dd className="mt-1 text-slate-200">{formatDate(item.createdAt)}</dd>
        </div>
        <div>
          <dt className="text-[11px] uppercase tracking-[0.18em] text-slate-500">Updated</dt>
          <dd className="mt-1 text-slate-200">{formatDate(item.updatedAt)}</dd>
        </div>
      </dl>
    </article>
  );
}
