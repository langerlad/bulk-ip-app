import React from 'react';
import '../styles/RawText.css';

const RawTextPage = () => {
  return (
    <div className="raw-text-container">
      <div className="raw-text-header">
        <h1>Raw IP Addresses</h1>
        <p>This page will be populated with the raw IP addresses.</p>
      </div>
      
      <div className="raw-text-content">
        <pre id="content">Loading content...</pre>
      </div>
      
      <div className="raw-text-actions">
        <button 
          className="btn btn-primary"
          onClick={() => window.print()}
        >
          Print
        </button>
        <button 
          className="btn btn-secondary"
          onClick={() => window.close()}
        >
          Close
        </button>
      </div>
    </div>
  );
};

export default RawTextPage;