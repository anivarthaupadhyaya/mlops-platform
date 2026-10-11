import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";

type Hit = { run_id: string; summary: string; score: number };

export default function SearchPage() {
  const [q, setQ] = useState("");
  const [hits, setHits] = useState<Hit[]>([]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    const response = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
    setHits(await response.json());
  }

  return (
    <section>
      <h2>Semantic search</h2>
      <form className="card" onSubmit={onSubmit} style={{ display: "flex", gap: 8 }}>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="high lr divergence, CIFAR accuracy…" />
        <button type="submit">Search</button>
      </form>
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
