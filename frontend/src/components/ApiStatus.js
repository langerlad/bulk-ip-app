import React from 'react';
import '../styles/ApiStatus.css';
import { format } from 'date-fns';

const ApiStatus = ({ apiStatus, clientIp }) => {
  // Format the reset time
  const formatResetTime = (resetTimeString) => {
    if (!resetTimeString) return 'Unknown';
    
    try {
      const resetDate = new Date(resetTimeString);
      return format(resetDate, 'yyyy-MM-dd HH:mm:ss');
    } catch (error) {
      console.error('Error parsing reset time:', error);
      return resetTimeString;
    }
  };
  
  // Get status class based on remaining requests
  const getStatusClass = (remaining) => {
    if (!remaining && remaining !== 0) return '';
    
    if (remaining <= 10) return 'danger';
    if (remaining <= 100) return 'warning';
    return 'good';
  };
  
  if (!apiStatus && !clientIp) {
    return null;
  }
  
  const totalLimit = apiStatus?.total_limit || 1000;
  const remaining = apiStatus?.remaining_requests || 0;
  
  return (
    <div className="api-status-container">
      <div className="api-info">
        <div className={`api-remaining ${getStatusClass(remaining)}`}>
          <span className="status-label">API Requests:</span> 
          <span className="status-value">{remaining}/{totalLimit} remaining today</span>
        </div>
        
        {apiStatus?.next_reset && (
          <div className="api-reset">
            <span className="status-label">Resets at:</span> 
            <span className="status-value">{formatResetTime(apiStatus.next_reset)} UTC</span>
          </div>
        )}
      </div>
      
      {clientIp && (
        <div className="client-ip">
          <span className="status-label">Your IP:</span> {clientIp}
        </div>
      )}
    </div>
  );
};

export default ApiStatus;