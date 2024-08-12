import { SearchBar } from "@/components/search-bar";
import { UnderstoodChips } from "@/components/understood-chips";
import { API_BASE } from "@/lib/api";

async function fetchResults(q: string) {
  if (!q) return null;
  const r = await fetch(`${API_BASE}/api/v1/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: q, limit: 20 }),
    cache: "no-store",
  });
  if (!r.ok) return null;
  return r.json();
}

export default async function SearchPage({ searchParams }: { searchParams: { q?: string } }) {
  const q = searchParams.q ?? "";
  const data = await fetchResults(q);
  return (
    <main className="mx-auto max-w-6xl px-4 py-10">
      <SearchBar initial={q} />
      <div className="mt-4">
        {data ? <UnderstoodChips parsed={data.parsed} relaxed={data.relaxed} /> : <p>Try a query above.</p>}
      </div>
      <div className="mt-6 text-sm text-muted-foreground">{data ? `${data.total} results for “${q}”` : ""}</div>
    </main>
  );
}
