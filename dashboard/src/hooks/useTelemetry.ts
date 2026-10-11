import { useEffect, useState } from "react";

export type TelemetryPoint = {
  node_id: string;
  ts: number;
  cpu: number;
  ram: number;
  gpu: number | null;
  gpu_mem: number | null;
};

export function useTelemetry(limit = 120): TelemetryPoint[] {
  const [points, setPoints] = useState<TelemetryPoint[]>([]);

  useEffect(() => {
    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${window.location.host}/ws/telemetry`);
    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data) as TelemetryPoint;
        setPoints((prev) => [...prev.slice(-(limit - 1)), payload]);
      } catch {
        /* ignore malformed frames */
      }
    };
    return () => ws.close();
  }, [limit]);

  return points;
}
