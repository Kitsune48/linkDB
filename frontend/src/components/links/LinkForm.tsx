import { useEffect, useState } from "react";

import { CategoryMultiSelect } from "./CategoryMultiSelect";
import type { LinkCategoryEntry, LinkFormValues } from "../../api/types";

type LinkFormProps = {
  initialValues?: LinkFormValues;
  categoryOptions: LinkCategoryEntry[];
  resetKey?: number;
  submitLabel: string;
  isSubmitting?: boolean;
  serverError?: string | null;
  onCancel?: () => void;
  onSubmit: (values: LinkFormValues) => Promise<void>;
};

type FieldErrors = Partial<Record<keyof LinkFormValues, string>>;

const defaultValues: LinkFormValues = {
  title: "",
  link: "",
  description: "",
  categories: [],
  status: "working",
};

export function LinkForm({
  initialValues,
  categoryOptions,
  resetKey = 0,
  submitLabel,
  isSubmitting = false,
  serverError,
  onCancel,
  onSubmit,
}: LinkFormProps) {
  const [values, setValues] = useState<LinkFormValues>(initialValues ?? defaultValues);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});

  useEffect(() => {
    setValues(initialValues ?? defaultValues);
    setFieldErrors({});
  }, [initialValues]);

  useEffect(() => {
    if (!initialValues) {
      setValues(defaultValues);
      setFieldErrors({});
    }
  }, [initialValues, resetKey]);

  function updateField<K extends keyof LinkFormValues>(key: K, value: LinkFormValues[K]) {
    setValues((current) => ({ ...current, [key]: value }));
    setFieldErrors((current) => ({ ...current, [key]: undefined }));
  }

  function validate() {
    const nextErrors: FieldErrors = {};

    if (!values.title.trim()) {
      nextErrors.title = "Title is required.";
    }

    if (!values.link.trim()) {
      nextErrors.link = "Link is required.";
    } else {
      try {
        new URL(values.link.trim());
      } catch {
        nextErrors.link = "Link must be a valid URL.";
      }
    }

    if (!values.description.trim()) {
      nextErrors.description = "Description is required.";
    }

    setFieldErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!validate()) {
      return;
    }

    await onSubmit({
      title: values.title.trim(),
      link: values.link.trim(),
      description: values.description.trim(),
      categories: values.categories,
      status: values.status,
    });
  }

  return (
    <form
      className="space-y-5 rounded-3xl border border-slate-800 bg-slate-900/90 p-5 shadow-lg shadow-slate-950/20 sm:p-6"
      onSubmit={handleSubmit}
    >
      <div className="grid gap-4 md:grid-cols-2">
        <label className="block">
          <span className="mb-1.5 block text-sm font-medium text-slate-300">Title</span>
          <input
            value={values.title}
            onChange={(event) => updateField("title", event.target.value)}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-brand-500"
            placeholder="Useful site or resource"
          />
          {fieldErrors.title ? (
            <span className="mt-1 block text-sm text-red-300">{fieldErrors.title}</span>
          ) : null}
        </label>

        <label className="block">
          <span className="mb-1.5 block text-sm font-medium text-slate-300">Link</span>
          <input
            value={values.link}
            onChange={(event) => updateField("link", event.target.value)}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-brand-500"
            placeholder="https://example.com"
          />
          {fieldErrors.link ? (
            <span className="mt-1 block text-sm text-red-300">{fieldErrors.link}</span>
          ) : null}
        </label>
      </div>

      <label className="block">
        <span className="mb-1.5 block text-sm font-medium text-slate-300">Description</span>
        <textarea
          value={values.description}
          onChange={(event) => updateField("description", event.target.value)}
          rows={4}
          className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-brand-500"
          placeholder="Short description to remember why this link matters"
        />
        {fieldErrors.description ? (
          <span className="mt-1 block text-sm text-red-300">{fieldErrors.description}</span>
        ) : null}
      </label>

      <div className="grid gap-4 md:grid-cols-2">
        <label className="block">
          <span className="mb-1.5 block text-sm font-medium text-slate-300">Status</span>
          <select
            value={values.status}
            onChange={(event) =>
              updateField("status", event.target.value as LinkFormValues["status"])
            }
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-slate-100 outline-none transition focus:border-brand-500"
          >
            <option value="down">Down</option>
            <option value="seized">Seized</option>
            <option value="unknown">Unknown</option>
            <option value="working">Working</option>
          </select>
        </label>
      </div>

      <CategoryMultiSelect
        label="Categories"
        description="Select one or more categories for this link."
        options={categoryOptions}
        value={values.categories}
        onChange={(nextCategories) => updateField("categories", nextCategories)}
      />

      {serverError ? (
        <p className="rounded-lg border border-red-900/70 bg-red-950/40 px-3 py-2 text-sm text-red-200">
          {serverError}
        </p>
      ) : null}

      <div className="flex flex-wrap gap-3">
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-xl bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isSubmitting ? "Saving..." : submitLabel}
        </button>
        {onCancel ? (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-xl border border-slate-700 px-4 py-2.5 text-sm text-slate-200 transition hover:bg-slate-800"
          >
            Cancel
          </button>
        ) : null}
      </div>
    </form>
  );
}
