import React from 'react';
import '../styles/Footer.css';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="footer">
      <div className="container footer-container">
        <div className="footer-info">
          <p>
            IP Checker uses the <a href="https://www.abuseipdb.com" target="_blank" rel="noopener noreferrer">AbuseIPDB</a> API to check IP addresses.
          </p>
          <p className="copyright">
            &copy; {currentYear} IP Checker. All rights reserved.
          </p>
        </div>
        
        <div className="footer-links">
          <a href="https://www.abuseipdb.com/api" target="_blank" rel="noopener noreferrer">
            API Documentation
          </a>
          <a href="https://www.abuseipdb.com/categories" target="_blank" rel="noopener noreferrer">
            Abuse Categories
          </a>
          <a href="https://www.abuseipdb.com/check" target="_blank" rel="noopener noreferrer">
            Check an IP
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;