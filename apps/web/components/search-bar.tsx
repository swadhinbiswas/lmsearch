"use client";
export function SearchBar() {
  return (
    <form action="/search" method="get" className="flex gap-2" role="search" aria-label="Product search">
      <input name="q" aria-label="Search products" placeholder="Ryzen laptop 32GB RAM under $1200…" className="w-full rounded-md border px-4 py-2" />
      <button type="submit" className="rounded-md bg-black px-4 py-2 text-white">Search</button>
    </form>
  );
}
