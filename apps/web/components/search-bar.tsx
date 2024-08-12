"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

const EXAMPLES = [
  "Ryzen laptop with 32GB RAM under $1200 for programming",
  "gaming phone, 120Hz screen, 5000mAh battery, below 40k BDT",
  "lightweight laptop i7 16GB around 100k BDT",
];

export function SearchBar({ initial = "" }: { initial?: string }) {
  const [q, setQ] = useState(initial);
  const router = useRouter();
  return (
    <div>
      <form
        role="search"
        aria-label="Product search"
        className="flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          router.push(`/search?q=${encodeURIComponent(q)}`);
        }}
      >
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          aria-label="Search products"
          placeholder="Ryzen laptop 32GB RAM under $1200…"
          className="w-full rounded-md border px-4 py-2"
        />
        <button type="submit" className="rounded-md bg-black px-4 py-2 text-white dark:bg-white dark:text-black">
          Search
        </button>
      </form>
      <div className="mt-2 flex flex-wrap gap-2">
        {EXAMPLES.map((ex) => (
          <button key={ex} onClick={() => setQ(ex)} className="rounded-full border px-2 py-0.5 text-xs" aria-label={`Use example: ${ex}`}>
            {ex.slice(0, 42)}…
          </button>
        ))}
      </div>
    </div>
  );
}
