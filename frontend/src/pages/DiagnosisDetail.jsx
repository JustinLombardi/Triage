import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";
import CategoryBadge from "../components/CategoryBadge.jsx";

export default function DiagnosisDetail() {
  const { id } = useParams();
  const [row, setRow] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let interval;
    async function load() {
      try {
        const data = await api.getDiagnosis(id);
        setRow(data);
        if (data.status !== "pending" && interval) clearInterval(interval);
      } catch (e) {
        setError(e.message);
        if (interval) clearInterval(interval);
      }
    }
    load();
    interval = setInterval(load, 2000);
    return () => clearInterval(interval);
  }, [id]);

  if (error) return <div className="panel panel-body">Couldn't load this diagnosis: {error}</div>;
  if (!row) return <div className="panel empty-state">Loading…</div>;

  return (
    <div className="panel">
      <div className="panel-head">
        <h2>{row.job_name || "unnamed check"}</h2>
      </div>
      <div className="panel-body">
        {row.status === "pending" && (
          <div className="empty-state" style={{ fontFamily: "var(--mono)" }}>
            Diagnosing…
          </div>
        )}

        {row.status === "error" && (
          <div style={{ color: "var(--accent-bug)" }}>
            Something went wrong: {row.error_message}
          </div>
        )}

        {row.status === "done" && (
          <>
            <div style={{ marginBottom: 14 }}>
              <CategoryBadge category={row.category} confidence={row.confidence} />
            </div>
            <p style={{ fontSize: 15, lineHeight: 1.5 }}>{row.summary}</p>

            {row.evidence && row.evidence.length > 0 && (
              <div className="diag-block">
                <h3>Evidence</h3>
                <div
                  className="evidence"
                  style={{ "--cat-color": "var(--accent-" + row.category + ")" }}
                >
                  {row.evidence.join("\n")}
                </div>
              </div>
            )}

            <div className="diag-block">
              <h3>Root cause</h3>
              <p>{row.root_cause}</p>
            </div>

            <div className="diag-block" style={{ borderTop: "1px solid var(--border)", paddingTop: 14 }}>
              <h3>Do this next</h3>
              <p style={{ fontWeight: 500 }}>{row.next_step}</p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
