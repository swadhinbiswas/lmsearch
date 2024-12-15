export type Category = "laptop" | "phone";
export interface MustFilters {
  ram_gb_min?: number | null;
  storage_gb_min?: number | null;
  cpu_series?: string[];
  refresh_hz_min?: number | null;
  battery_mah_min?: number | null;
}
export interface StructuredQuery {
  category?: Category | null;
  brands: string[];
  must: MustFilters;
  price: { min?: number | null; max?: number | null; currency: string };
  use_case: string[];
  soft_preferences: string[];
  exclude: string[];
  semantic_query: string;
}
export interface ProductHit {
  id: number; title: string; brand: string; category: string;
  price: number; currency: string; url: string; image: string;
  rating: number; match_score: number;
  explanation: { matched: string[]; partial: string[]; missing: string[] };
}
