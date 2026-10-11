import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useTelemetry } from "../hooks/useTelemetry";

export default function LiveTelemetry() {
  const points = useTelemetry();
  const data = points.map((p) => ({
    t: new Date(p.ts * 1000).toLocaleTimeString(),
    cpu: p.cpu,
    ram: p.ram,
    gpu: p.gpu ?? 0,
  }));

  return (
    <section>
      <h2>Live host telemetry</h2>
      <p className="muted">CPU / RAM / GPU from the host agent over Redis pubsub.</p>
      <div className="card" style={{ height: 360 }}>
        <ResponsiveContainer>
          <LineChart data={data}>
            <XAxis dataKey="t" hide />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Line type="monotone" dataKey="cpu" stroke="#6ee7b7" dot={false} />
            <Line type="monotone" dataKey="ram" stroke="#93c5fd" dot={false} />
            <Line type="monotone" dataKey="gpu" stroke="#fbbf24" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
