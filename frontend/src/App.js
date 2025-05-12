import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Pages
import IPFormPage from './pages/IPFormPage';
import ResultsPage from './pages/ResultsPage';
import ErrorPage from './pages/ErrorPage';
import RawTextPage from './pages/RawTextPage';

// Components
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Styles
import './styles/App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<IPFormPage />} />
            <Route path="/results" element={<ResultsPage />} />
            <Route path="/error" element={<ErrorPage />} />
            <Route path="/raw" element={<RawTextPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
        <Footer />
        <ToastContainer position="bottom-right" autoClose={5000} />
      </div>
    </Router>
  );
}

export default App;