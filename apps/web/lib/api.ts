export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export type ProductHit = {
  id: number; title: string; brand: string; category: string;
  price: number; currency: string; url: string; image: string;
  rating: number; match_score: number;
  explanation: { matched: string[]; partial: string[]; missing: string[] };
};

export async function runSearch(query: string, limit = 20) {
  const r = await fetch(`${API_BASE}/api/v1/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, limit }),
  });
  if (!r.ok) throw new Error(`search failed: ${r.status}`);
  return r.json();
}
