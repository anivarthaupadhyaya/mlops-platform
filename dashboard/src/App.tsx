import { NavLink, Route, Routes } from "react-router-dom";
import LiveTelemetry from "./pages/LiveTelemetry";
import Experiments from "./pages/Experiments";
import ExperimentRuns from "./pages/ExperimentRuns";
import RunDetail from "./pages/RunDetail";
import SnapshotView from "./pages/SnapshotView";
import SearchPage from "./pages/SearchPage";

export default function App() {
  return (
    <div className="layout">
      <nav>
        <h1>MLOps</h1>
        <NavLink to="/" end>
          Telemetry
        </NavLink>
        <NavLink to="/experiments">Experiments</NavLink>
        <NavLink to="/search">Search</NavLink>
      </nav>
      <main>
        <Routes>
          <Route path="/" element={<LiveTelemetry />} />
          <Route path="/experiments" element={<Experiments />} />
          <Route path="/experiments/:experimentId" element={<ExperimentRuns />} />
          <Route path="/runs/:runId" element={<RunDetail />} />
          <Route path="/snapshots/:snapshotId" element={<SnapshotView />} />
          <Route path="/search" element={<SearchPage />} />
        </Routes>
      </main>
    </div>
  );
}
