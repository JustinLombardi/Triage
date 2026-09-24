import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

export default function NewDiagnosis() {
  const [jobName, setJobName] = useState("");
  const [seenBefore, setSeenBefore] = useState(false);
  const [logText, setLogText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    if (!logText.trim()) {
      setError("Paste some log output first.");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      const row = await api.createDiagnosis({
        job_name: jobName || null,
        log_text: logText,
        seen_before: seenBefore,
      });
      navigate(`/diagnoses/${row.id}`);
    } catch (e) {
      setError(e.message);
      setSubmitting(false);
    }
  }

  return (
    <form className="panel" onSubmit={handleSubmit}>
      <div className="panel-head">
        <h2>New diagnosis</h2>
      </div>
      <div className="panel-body">
        <div className="field">
          <label htmlFor="job-name">Job or check name (optional)</label>
          <input
            id="job-name"
            type="text"
            value={jobName}
            onChange={(e) => setJobName(e.target.value)}
            placeholder="e.g. test (unit, node-18)"
          />
        </div>
        <label className="toggle-row">
          <input
            type="checkbox"
            checked={seenBefore}
            onChange={(e) => setSeenBefore(e.target.checked)}
          />
          This check has failed before on this branch or PR
        </label>
        <div className="field">
          <label htmlFor="log">Failed job log</label>
          <textarea
            id="log"
            className="code"
            value={logText}
            onChange={(e) => setLogText(e.target.value)}
            placeholder="Paste the log output from the failed step — copy it from the Actions run page."
          />
        </div>
        {error && <div style={{ color: "var(--accent-bug)", marginBottom: 12 }}>{error}</div>}
        <button className="run" type="submit" disabled={submitting}>
          {submitting ? "Queuing…" : "Diagnose"}
        </button>
      </div>
    </form>
  );
}
