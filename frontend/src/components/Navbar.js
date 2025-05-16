import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import '../styles/Navbar.css';

const Navbar = () => {
  
  return (
    <nav className="navbar">
      <div className="container navbar-container">
        <Link to="/" className="navbar-brand">
          <span className="logo-icon">🔍</span>
          <span className="logo-text">IP Address Checker</span>
        </Link>
        
        <div className="navbar-links">
          <a 
            href="https://www.abuseipdb.com" 
            target="_blank" 
            rel="noopener noreferrer"
            className="nav-link external"
          >
            AbuseIPDB <span className="external-icon">↗</span>
          </a>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;