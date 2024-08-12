"use client";
import { Badge } from "@/components/ui/badge";

export type Parsed = {
  category?: string | null;
  brands?: string[];
  must?: Record<string, unknown>;
  price?: { min?: number | null; max?: number | null; currency?: string };
  use_case?: string[];
  relaxed?: string[];
};

export function UnderstoodChips({ parsed, relaxed }: { parsed: Parsed; relaxed?: string[] }) {
  const chips: string[] = [];
  if (parsed.category) chips.push(`category: ${parsed.category}`);
  for (const b of parsed.brands ?? []) chips.push(b);
  const must = parsed.must ?? {};
  if (must.ram_gb_min) chips.push(`${must.ram_gb_min}GB RAM`);
  if (must.storage_gb_min) chips.push(`${must.storage_gb_min}GB storage`);
  if (Array.isArray(must.cpu_series)) for (const c of must.cpu_series) chips.push(String(c));
  if (must.refresh_hz_min) chips.push(`${must.refresh_hz_min}Hz`);
  if (must.battery_mah_min) chips.push(`${must.battery_mah_min}mAh`);
  if (parsed.price?.max) chips.push(`under ${parsed.price.max} ${parsed.price.currency ?? "USD"}`);
  for (const u of parsed.use_case ?? []) chips.push(`for ${u}`);
  return (
    <div className="flex flex-wrap gap-2" aria-label="Understood filters">
      {chips.map((c) => (
        <Badge key={c}>{c}</Badge>
      ))}
      {(relaxed ?? []).map((r) => (
        <Badge key={r} className="border-dashed">relaxed: {r}</Badge>
      ))}
      {chips.length === 0 && <span className="text-sm text-muted-foreground">Showing semantic matches</span>}
    </div>
  );
}
