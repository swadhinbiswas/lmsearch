import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { API_BASE } from "@/lib/api";

async function getProduct(id: string) {
  const r = await fetch(`${API_BASE}/api/v1/products/${id}`, { cache: "no-store" });
  if (!r.ok) return null;
  return r.json();
}

export default async function ProductPage({ params }: { params: { id: string } }) {
  const p = await getProduct(params.id);
  if (!p) return <main className="p-10">Product not found.</main>;
  return (
    <main className="mx-auto max-w-4xl px-4 py-10">
      <h1 className="text-2xl font-bold">{p.title}</h1>
      <div className="mt-2 text-lg">${p.price} {p.currency} · ★ {p.rating}</div>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={p.image || "/placeholder.png"} alt={p.title} className="mt-4 h-72 w-full rounded object-cover" />
      <Card className="mt-4">
        <h2 className="font-semibold">Why it matches</h2>
        <ul className="mt-2 list-disc pl-5 text-sm">
          {(p.explanation?.matched ?? []).map((m: string) => <li key={m}>{m}</li>)}
        </ul>
      </Card>
      <Card className="mt-4">
        <h2 className="font-semibold">Full specs</h2>
        <dl className="mt-2 grid grid-cols-2 gap-2 text-sm">
          {Object.entries(p.specs ?? {}).map(([k, v]) => (
            <div key={k} className="flex justify-between border-b py-1">
              <dt className="text-muted-foreground">{k}</dt>
              <dd>{String(v)}</dd>
            </div>
          ))}
        </dl>
      </Card>
      <div className="mt-4 flex gap-2">
        <a href={p.url} target="_blank" rel="noreferrer" className="rounded-md bg-black px-4 py-2 text-white">View store</a>
        <a href={`/compare?ids=${p.id}`} className="rounded-md border px-4 py-2">Compare</a>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <Badge>{p.brand}</Badge>
        <Badge>{p.category}</Badge>
      </div>
    </main>
  );
}
