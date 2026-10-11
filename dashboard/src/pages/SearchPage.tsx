import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";

type Hit = { run_id: string; summary: string; score: number };

export default function SearchPage() {
  const [q, setQ] = useState("");
  const [hits, setHits] = useState<Hit[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    const query = q.trim();
    if (!query || loading) return;
    setLoading(true);
    setSearched(true);
    setError(null);
    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
      const text = await response.text();
      let payload: unknown = null;
      try {
        payload = text ? JSON.parse(text) : null;
      } catch {
        throw new Error(response.ok ? "Search returned invalid JSON" : `Search failed (${response.status})`);
      }
      if (!response.ok) {
        const detail =
          payload && typeof payload === "object" && "detail" in payload ? String((payload as { detail: unknown }).detail) : text;
        throw new Error(detail || `Search failed (${response.status})`);
      }
      if (!Array.isArray(payload)) {
        throw new Error("Search returned an unexpected payload");
      }
      setHits(payload as Hit[]);
    } catch (err) {
      setHits([]);
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <h2>Semantic search</h2>
      <form className="card" onSubmit={onSubmit} style={{ display: "flex", gap: 8 }}>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="high lr divergence, CIFAR accuracy…" />
        <button type="submit" disabled={loading || !q.trim()}>
          {loading ? "Searching…" : "Search"}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      {!error && !loading && searched && hits.length === 0 && (
        <p className="muted">No indexed runs matched. Index a run, then search again.</p>
      )}
      {hits.map((hit) => (
        <div className="card" key={hit.run_id}>
          <Link to={`/runs/${hit.run_id}`}>{hit.run_id}</Link>
          <p>{hit.summary}</p>
          <p className="muted">score {hit.score.toFixed(3)}</p>
        </div>
      ))}
    </section>
  );
}
