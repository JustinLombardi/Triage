import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import CategoryBadge from "../components/CategoryBadge.jsx";

export default function Dashboard() {
  const [rows, setRows] = useState(null);
  const [error, setError] = useState(null);

  async function load() {
    try {
      const data = await api.listDiagnoses();
      setRows(data);
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="panel">
      <div className="panel-head">
        <h2>Recent diagnoses</h2>
      </div>
      {error && <div className="panel-body">Couldn't load diagnoses: {error}</div>}
      {!error && rows === null && <div className="empty-state">Loading…</div>}
      {rows && rows.length === 0 && (
        <div className="empty-state">
          Nothing here yet. Paste a failed log to run your first diagnosis.
        </div>
      )}
      {rows &&
        rows.map((row) => (
          <Link key={row.id} to={`/diagnoses/${row.id}`} className="list-row">
            <div>
              <div style={{ fontWeight: 500, marginBottom: 4 }}>
                {row.job_name || "unnamed check"}
                {row.repo && <span className="meta"> · {row.repo}</span>}
              </div>
              {row.status === "done" ? (
                <CategoryBadge category={row.category} confidence={row.confidence} />
              ) : (
                <span className="status-pill">{row.status}…</span>
              )}
            </div>
            <div className="meta">{new Date(row.created_at).toLocaleString()}</div>
          </Link>
        ))}
    </div>
  );
}
