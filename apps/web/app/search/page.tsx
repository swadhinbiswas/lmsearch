"use client";
import { useEffect, useState } from "react";
import { Facets, type FacetState } from "@/components/facets";
import { ResultsGrid } from "@/components/product-card";
import { SearchBar } from "@/components/search-bar";
import { UnderstoodChips } from "@/components/understood-chips";
import { runSearch, type ProductHit } from "@/lib/api";
import { useSearchParams } from "next/navigation";

export default function SearchPage() {
  const sp = useSearchParams();
  const q = sp.get("q") ?? "";
  const [hits, setHits] = useState<ProductHit[]>([]);
  const [parsed, setParsed] = useState<Record<string, never> | Record<string, unknown>>({});
  const [relaxed, setRelaxed] = useState<string[]>([]);
  const [facets, setFacets] = useState<FacetState>({ brands: [], maxPrice: null, minRam: null, category: null });

  useEffect(() => {
    if (!q) return;
    runSearch(q, 30).then((d) => {
      setHits(d.hits);
      setParsed(d.parsed);
      setRelaxed(d.relaxed ?? []);
    }).catch(() => undefined);
  }, [q]);

  const brands = [...new Set(hits.map((h) => h.brand))].slice(0, 12);
  const filtered = hits.filter((h) => {
    if (facets.brands.length && !facets.brands.includes(h.brand)) return false;
    if (facets.maxPrice && h.price > facets.maxPrice) return false;
    return true;
  });

  return (
    <main className="mx-auto max-w-6xl px-4 py-10">
      <SearchBar initial={q} />
      <div className="mt-4">
        <UnderstoodChips parsed={parsed as never} relaxed={relaxed} />
      </div>
      <div className="mt-6 flex flex-col gap-4 lg:flex-row">
        <Facets value={facets} onChange={setFacets} brands={brands} />
        <div className="flex-1">
          <ResultsGrid hits={filtered} />
        </div>
      </div>
    </main>
  );
}
