import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import CurtainCalculator from './components/CurtainCalculator';
import DesignManager from './components/DesignManager';
import MaterialTypeManager from './components/MaterialTypeManager';
import MaterialReferenceManager from './components/MaterialReferenceManager';
import ColorManager from './components/ColorManager';
import OrderList from './components/OrdersList';
import ProfitabilityManager from './components/ProfitabilityManager';

const Layout = ({ children }) => {
  return (
    <div>
      <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
        <div className="container">
          <span className="navbar-brand">Sistema de Cortinas</span>
          <button 
            className="navbar-toggler" 
            type="button" 
            data-bs-toggle="collapse" 
            data-bs-target="#navbarNav"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav">
              <li className="nav-item">
                <Link to="/" className="nav-link">Cotizar Cortina</Link>
              </li>
              <li className="nav-item">
                <Link to="/designs" className="nav-link">Gestión de Diseños</Link>
              </li>
              <li className="nav-item">
                <Link to="/material-types" className="nav-link">Tipos de Insumos</Link>
              </li>
              <li className="nav-item">
                <Link to="/material-references" className="nav-link">Referencias de Insumos</Link>
              </li>
              <li className="nav-item">
                <Link to="/colors" className="nav-link">Colores</Link>
              </li>
              <li className="nav-item">
                <Link to="/orders" className="nav-link">Órdenes</Link>
              </li>
              <li className="nav-item">
                <Link to="/profitability" className="nav-link">Rentabilidad</Link>
              </li>
            </ul>
          </div>
        </div>
      </nav>
      <main className="container py-4">
        {children}
      </main>
      <footer className="footer mt-auto py-3 bg-light">
        <div className="container text-center">
          <span className="text-muted">Sistema de Gestión de Cortinas © 2024</span>
        </div>
      </footer>
    </div>
  );
};

const App = () => {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<CurtainCalculator />} />
          <Route path="/designs" element={<DesignManager />} />
          <Route path="/material-types" element={<MaterialTypeManager />} />
          <Route path="/material-references" element={<MaterialReferenceManager />} />
          <Route path="/colors" element={<ColorManager />} />
          <Route path="/orders" element={<OrderList />} />
          <Route path="/profitability" element={<ProfitabilityManager />} />
        </Routes>
      </Layout>
    </Router>
  );
};

export default App;