import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Planner from "./pages/Planner/Planner";
import "./App.css";

const Layout = ({ children }: { children: React.ReactNode }) => (
  <div className="app-container">
    <nav className="top-menu">
      <Link to="/">Home</Link>
      <Link to="/planner">Route Planner</Link>
      <Link to="/contact">Contact</Link>
    </nav>
    <main className="main-content">{children}</main>
  </div>
);

export default function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route
            path="/"
            element={
              <div>
                <h1>Home</h1>
              </div>
            }
          />
          <Route path="/planner" element={<Planner />} />
          <Route
            path="/contact"
            element={
              <div>
                <h1>Contact</h1>
              </div>
            }
          />
        </Routes>
      </Layout>
    </Router>
  );
}
