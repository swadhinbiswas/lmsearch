"use client";
import { useState } from "react";

export type FacetState = { brands: string[]; maxPrice: number | null; minRam: number | null; category: string | null };

export function Facets({
  value, onChange, brands,
}: {
  value: FacetState;
  onChange: (v: FacetState) => void;
  brands: string[];
}) {
  const [open, setOpen] = useState(true);
  return (
    <aside aria-label="Search facets" className="w-full shrink-0 rounded-lg border p-4 lg:w-60">
      <button onClick={() => setOpen(!open)} aria-expanded={open} className="font-semibold">
        Filters
      </button>
      {open && (
        <div className="mt-3 space-y-4">
          <fieldset>
            <legend className="text-sm font-medium">Brand</legend>
            {brands.map((b) => (
              <label key={b} className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={value.brands.includes(b)}
                  onChange={(e) =>
                    onChange({
                      ...value,
                      brands: e.target.checked ? [...value.brands, b] : value.brands.filter((x) => x !== b),
                    })
                  }
                />
                {b}
              </label>
            ))}
          </fieldset>
          <div>
            <label htmlFor="maxprice" className="text-sm font-medium">Max price (USD): {value.maxPrice ?? "any"}</label>
            <input
              id="maxprice"
              type="range"
              min={200}
              max={3000}
              step={50}
              value={value.maxPrice ?? 3000}
              onChange={(e) => onChange({ ...value, maxPrice: Number(e.target.value) })}
              className="w-full"
            />
          </div>
          <div>
            <label htmlFor="minram" className="text-sm font-medium">Min RAM</label>
            <select
              id="minram"
              value={value.minRam ?? ""}
              onChange={(e) => onChange({ ...value, minRam: e.target.value ? Number(e.target.value) : null })}
              className="w-full rounded border px-2 py-1"
            >
              <option value="">Any</option>
              <option value="8">8GB+</option>
              <option value="16">16GB+</option>
              <option value="32">32GB+</option>
            </select>
          </div>
        </div>
      )}
    </aside>
  );
}
