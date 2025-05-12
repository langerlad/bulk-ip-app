import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import '../styles/Error.css';

const ErrorPage = () => {
  const location = useLocation();
  const { errorMessage, invalidIps } = location.state || {};
  
  return (
    <div className="container">
      <div className="error-container">
        <h1>Error</h1>
        
        <div className="error-message">
          <p>Sorry, but an error has occurred:</p>
          <p className="message">{errorMessage || 'Unknown error'}</p>
          
          {invalidIps && invalidIps.length > 0 && (
            <div className="invalid-ips">
              <h3>Invalid IP addresses:</h3>
              <ul>
                {invalidIps.map((ip, index) => (
                  <li key={index}>{ip}</li>
                ))}
              </ul>
              <p>Please correct these IP addresses and try again.</p>
            </div>
          )}
        </div>
        
        <div className="action-buttons">
          <Link to="/check" className="btn btn-primary">
            Return to IP Checker
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ErrorPage;