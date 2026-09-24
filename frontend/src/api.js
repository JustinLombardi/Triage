const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return res.json();
}

export const api = {
  listDiagnoses: (limit = 25) => request(`/api/diagnoses?limit=${limit}`),
  getDiagnosis: (id) => request(`/api/diagnoses/${id}`),
  createDiagnosis: (payload) =>
    request("/api/diagnoses", { method: "POST", body: JSON.stringify(payload) }),
};
