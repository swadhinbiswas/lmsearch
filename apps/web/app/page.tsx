import { SearchBar } from "@/components/search-bar";

export default function Home() {
  return (
    <main className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="text-3xl font-bold">lmsearch</h1>
      <p className="mt-2 text-muted-foreground">Describe the product you want in plain words.</p>
      <div className="mt-6">
        <SearchBar />
      </div>
    </main>
  );
}
