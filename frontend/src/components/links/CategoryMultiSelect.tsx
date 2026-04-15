import type { LinkCategory, LinkCategoryEntry } from "../../api/types";

type CategoryMultiSelectProps = {
  label: string;
  description?: string;
  options: LinkCategoryEntry[];
  value: LinkCategory[];
  onChange: (categories: LinkCategory[]) => void;
};

export function CategoryMultiSelect({
  label,
  description,
  options,
  value,
  onChange,
}: CategoryMultiSelectProps) {
  function toggleCategory(category: LinkCategory) {
    onChange(
      value.includes(category)
        ? value.filter((current) => current !== category)
        : [...value, category],
    );
  }

  return (
    <fieldset className="space-y-3 rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
      <div className="space-y-1">
        <legend className="text-sm font-medium text-slate-300">{label}</legend>
        {description ? <p className="text-xs leading-5 text-slate-500">{description}</p> : null}
      </div>

      <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
        {options.map((option) => (
          <label
            key={option.slug}
            className="flex cursor-pointer items-start gap-3 rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-200 transition hover:border-slate-700"
          >
            <input
              type="checkbox"
              checked={value.includes(option.slug)}
              onChange={() => toggleCategory(option.slug)}
              className="mt-0.5 h-4 w-4 rounded border-slate-600 bg-slate-950 text-brand-500"
            />
            <span>{option.label}</span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}
