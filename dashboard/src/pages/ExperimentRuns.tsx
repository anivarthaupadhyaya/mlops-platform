import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

type Run = { id: string; status: string; snapshot_id: string; started_at: string };

export default function ExperimentRuns() {
  const { experimentId } = useParams();
  const [runs, setRuns] = useState<Run[]>([]);

  useEffect(() => {
    if (!experimentId) return;
    fetch(`/api/experiments/${experimentId}/runs`)
      .then((r) => r.json())
      .then(setRuns)
      .catch(() => setRuns([]));
  }, [experimentId]);

  return (
    <section>
      <h2>Runs</h2>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Run</th>
              <th>Status</th>
              <th>Snapshot</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr key={run.id}>
                <td>
                  <Link to={`/runs/${run.id}`}>{run.id.slice(0, 8)}</Link>
                </td>
                <td>{run.status}</td>
                <td>
                  <Link to={`/snapshots/${run.snapshot_id}`}>{run.snapshot_id.slice(0, 12)}</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
