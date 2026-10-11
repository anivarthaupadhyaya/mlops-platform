import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type Series = Record<string, { step: number; value: number }[]>;
type Run = { id: string; status: string; snapshot_id: string; params: Record<string, unknown> };

export default function RunDetail() {
  const { runId } = useParams();
  const [run, setRun] = useState<Run | null>(null);
  const [metrics, setMetrics] = useState<Series>({});

  useEffect(() => {
    if (!runId) return;
    fetch(`/api/runs/${runId}`)
      .then((r) => r.json())
      .then(setRun)
      .catch(() => setRun(null));
    fetch(`/api/runs/${runId}/metrics`)
      .then((r) => r.json())
      .then(setMetrics)
      .catch(() => setMetrics({}));
  }, [runId]);

  return (
    <section>
      <h2>Run {runId?.slice(0, 8)}</h2>
      {run && (
        <p className="muted">
          {run.status} · snapshot <Link to={`/snapshots/${run.snapshot_id}`}>{run.snapshot_id.slice(0, 12)}</Link>
        </p>
      )}
      {Object.entries(metrics).map(([name, points]) => (
        <div className="card" key={name} style={{ height: 280 }}>
          <h3>{name}</h3>
          <ResponsiveContainer>
            <LineChart data={points}>
              <XAxis dataKey="step" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#6ee7b7" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ))}
    </section>
  );
}
