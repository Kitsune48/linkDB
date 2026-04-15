import { useState } from "react";

import { CategoryMultiSelect } from "./CategoryMultiSelect";
import type { LinkCategory, LinkCategoryEntry, LinkStatus } from "../../api/types";

type LinksFiltersProps = {
  initialQuery: string;
  initialCategories: LinkCategory[];
  initialStatus: LinkStatus | "";
  initialAddedByMe: boolean;
  categoryOptions: LinkCategoryEntry[];
  onApply: (filters: {
    q: string;
    categories: LinkCategory[];
    status: LinkStatus | "";
    addedByMe: boolean;
  }) => void;
};

export function LinksFilters({
  initialQuery,
  initialCategories,
  initialStatus,
  initialAddedByMe,
  categoryOptions,
  onApply,
}: LinksFiltersProps) {
  const [query, setQuery] = useState(initialQuery);
  const [categories, setCategories] = useState<LinkCategory[]>(initialCategories);
  const [status, setStatus] = useState<LinkStatus | "">(initialStatus);
  const [addedByMe, setAddedByMe] = useState(initialAddedByMe);

  return (
    <form
      className="space-y-4 rounded-3xl border border-slate-800 bg-slate-900/90 p-4 shadow-lg shadow-slate-950/20"
      onSubmit={(event) => {
        event.preventDefault();
        onApply({ q: query.trim(), categories, status, addedByMe });
      }}
    >
      <input
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Search by title, description or link"
        className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-brand-500"
      />

      <CategoryMultiSelect
        label="Filter categories"
        options={categoryOptions}
        value={categories}
        onChange={setCategories}
      />

      <div className="grid gap-3 md:grid-cols-[1fr_auto_auto]">
        <select
          value={status}
          onChange={(event) => setStatus(event.target.value as LinkStatus | "")}
          className="rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-sm text-slate-100 outline-none transition focus:border-brand-500"
        >
          <option value="">All statuses</option>
          <option value="down">Down</option>
          <option value="seized">Seized</option>
          <option value="unknown">Unknown</option>
          <option value="working">Working</option>
        </select>

        <label className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-sm text-slate-200">
          <input
            type="checkbox"
            checked={addedByMe}
            onChange={(event) => setAddedByMe(event.target.checked)}
            className="h-4 w-4 rounded border-slate-600 bg-slate-950 text-brand-500"
          />
          Added by me
        </label>

        <button
          type="submit"
          className="rounded-xl bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-700"
        >
          Apply
        </button>
      </div>
    </form>
  );
}
