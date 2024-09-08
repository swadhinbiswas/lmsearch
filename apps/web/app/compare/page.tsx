"use client";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";

export default function ComparePage() {
  const sp = useSearchParams();
  const ids = (sp.get("ids") ?? "").split(",").filter(Boolean).slice(0, 3);
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  useEffect(() => {
    Promise.all(ids.map((id) => fetch(`${API_BASE}/api/v1/products/${id}`).then((r) => r.json()))).then(
      (v) => setRows(v as Record<string, unknown>[]),
    );
  }, [sp]);
  if (!ids.length) return <main className="p-10">Add ?ids=1,2 to compare.</main>;
  const keys = [...new Set(rows.flatMap((r) => Object.keys((r as { specs?: object }).specs ?? {})))];
  return (
    <main className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="text-2xl font-bold">Compare</h1>
      <table className="mt-4 w-full border text-sm">
        <thead>
          <tr>
            <th className="border p-2 text-left">Spec</th>
            {rows.map((r: unknown, i: number) => (
              <th key={i} className="border p-2 text-left">{String((r as { title?: string }).title ?? ids[i])}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {keys.map((k) => (
            <tr key={k}>
              <td className="border p-2">{k}</td>
              {rows.map((r: unknown, i: number) => (
                <td key={i} className="border p-2">{String(((r as { specs?: Record<string, unknown> }).specs ?? {})[k] ?? "—")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
