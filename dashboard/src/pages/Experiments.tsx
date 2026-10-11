import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

type Experiment = { id: string; name: string; description: string | null; created_at: string };

export default function Experiments() {
  const [rows, setRows] = useState<Experiment[]>([]);

  useEffect(() => {
    fetch("/api/experiments")
      .then((r) => r.json())
      .then(setRows)
      .catch(() => setRows([]));
  }, []);

  return (
    <section>
      <h2>Experiments</h2>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id}>
                <td>
                  <Link to={`/experiments/${row.id}`}>{row.name}</Link>
                </td>
                <td>{row.description ?? "—"}</td>
                <td>{new Date(row.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
