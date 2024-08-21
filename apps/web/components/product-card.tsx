import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { ProductHit } from "@/lib/api";

export function ProductCard({ hit }: { hit: ProductHit }) {
  return (
    <Card className="flex flex-col gap-2">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={hit.image || "/placeholder.png"} alt={hit.title} className="h-40 w-full rounded object-cover" loading="lazy" />
      <div className="text-sm font-semibold">{hit.title}</div>
      <div className="text-sm">
        ${hit.price.toFixed(0)} <span className="text-muted-foreground">{hit.currency}</span>
        <span className="ml-2">★ {hit.rating.toFixed(1)}</span>
      </div>
      <div className="flex flex-wrap gap-1">
        {(hit.explanation.matched ?? []).slice(0, 3).map((m) => (
          <Badge key={m}>{m.slice(0, 40)}</Badge>
        ))}
      </div>
      <div className="mt-auto flex items-center justify-between">
        <span className="text-xs text-muted-foreground">match {(hit.match_score * 100).toFixed(0)}%</span>
        <a href={hit.url} className="text-sm underline" target="_blank" rel="noreferrer">View store</a>
      </div>
    </Card>
  );
}

export function ProductSkeleton() {
  return <div className="h-64 animate-pulse rounded-lg bg-muted" aria-label="Loading product" />;
}

export function ResultsGrid({ hits }: { hits: ProductHit[] }) {
  if (!hits.length) return <p className="text-muted-foreground">No products match. Try relaxing a filter.</p>;
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3" role="list">
      {hits.map((h) => (
        <div key={h.id} role="listitem">
          <ProductCard hit={h} />
        </div>
      ))}
    </div>
  );
}
