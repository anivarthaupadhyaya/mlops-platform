import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

type Snapshot = {
  id: string;
  python_version: string;
  packages: Record<string, string>;
  image_digest: string | null;
  config: Record<string, unknown>;
  created_at: string;
};

export default function SnapshotView() {
  const { snapshotId } = useParams();
  const [snap, setSnap] = useState<Snapshot | null>(null);

  useEffect(() => {
    if (!snapshotId) return;
    fetch(`/api/snapshots/${snapshotId}`)
      .then((r) => r.json())
      .then(setSnap)
      .catch(() => setSnap(null));
  }, [snapshotId]);

  if (!snap) return <p className="muted">Loading snapshot…</p>;

  return (
    <section>
      <h2>Snapshot</h2>
      <div className="card">
        <p>
          <strong>id</strong> {snap.id}
        </p>
        <p>
          <strong>python</strong> {snap.python_version}
        </p>
        <p>
          <strong>image</strong> {snap.image_digest ?? "—"}
        </p>
        <h3>Config</h3>
        <pre>{JSON.stringify(snap.config, null, 2)}</pre>
        <h3>Packages</h3>
        <pre>{JSON.stringify(snap.packages, null, 2)}</pre>
      </div>
    </section>
  );
}
