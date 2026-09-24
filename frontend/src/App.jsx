import { NavLink, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard.jsx";
import NewDiagnosis from "./pages/NewDiagnosis.jsx";
import DiagnosisDetail from "./pages/DiagnosisDetail.jsx";

export default function App() {
  return (
    <div className="wrap">
      <header className="top">
        <div className="brand">
          <NavLink to="/"><h1>triage</h1></NavLink>
          <p>CI failure diagnosis</p>
        </div>
        <nav className="top-nav">
          <NavLink to="/" end>Dashboard</NavLink>
          <NavLink to="/new">New diagnosis</NavLink>
        </nav>
      </header>

      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/new" element={<NewDiagnosis />} />
        <Route path="/diagnoses/:id" element={<DiagnosisDetail />} />
      </Routes>
    </div>
  );
}
