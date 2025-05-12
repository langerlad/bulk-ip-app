import React, { useState } from 'react';
import '../styles/IPResultCard.css';
import { formatDistanceToNow, parseISO } from 'date-fns';

const IPResultCard = ({ result, showComments }) => {
  const [commentsVisible, setCommentsVisible] = useState(false);
  
  // Determine severity class based on abuse score
  const getSeverityClass = (score) => {
    const abuseScore = parseInt(score || 0);
    if (abuseScore >= 75) return 'danger';
    if (abuseScore >= 30) return 'warning';
    return 'safe';
  };
  
  // Format array or string property for display
  const formatProperty = (prop) => {
    if (prop === null || prop === undefined) return 'Unknown';
    if (Array.isArray(prop)) {
      return prop.length > 0 ? prop.join(', ') : 'None';
    }
    return prop;
  };
  
  // Format date to human readable format with relative time
  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    try {
      const date = parseISO(dateString);
      const formattedDate = date.toLocaleString();
      const timeAgo = formatDistanceToNow(date, { addSuffix: true });
      return `${formattedDate} (${timeAgo})`;
    } catch (error) {
      return dateString;
    }
  };
  
  // Handle displaying of report comments
  const toggleComments = () => {
    setCommentsVisible(!commentsVisible);
  };
  
  // Render error state if needed
  if (result.error) {
    return (
      <div className="ip-card error">
        <div className="ip-header">
          <div>{result.ipAddress}</div>
          <div>Error</div>
        </div>
        <div className="ip-body">
          <p className="error-message">{result.error}</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className={`ip-card ${getSeverityClass(result.abuseConfidenceScore)}`}>
      <div className="ip-header">
        <div>{result.ipAddress}</div>
        <div>Abuse Score: {result.abuseConfidenceScore || 0}%</div>
      </div>
      
      <div className="ip-body">
        {/* Status tags */}
        <div className="status-tags">
          {result.isTor && <span className="status-tag tor">Tor Exit Node</span>}
          {result.isPublic === false && <span className="status-tag private">Private IP</span>}
          {result.isWhitelisted && <span className="status-tag whitelisted">Whitelisted</span>}
        </div>
        
        <div className="ip-details">
          <div className="detail-row">
            <div className="detail-item">
              <span className="detail-label">Country: </span> 
              {formatProperty(result.countryName)} {result.countryCode ? `(${result.countryCode})` : ''}
            </div>
            
            <div className="detail-item">
              <span className="detail-label">ISP: </span> 
              {formatProperty(result.isp)}
            </div>
          </div>
          
          <div className="detail-row">
            <div className="detail-item">
              <span className="detail-label">Domain: </span> 
              {formatProperty(result.domain)}
            </div>
            
            <div className="detail-item">
              <span className="detail-label">Usage Type: </span> 
              {formatProperty(result.usageType)}
            </div>
          </div>
          
          <div className="detail-row">
            <div className="detail-item">
              <span className="detail-label">Hostnames: </span> 
              {formatProperty(result.hostnames)}
            </div>
          </div>
          
          <div className="detail-row reports-row">
            <div className="detail-item">
              <span className="detail-label">Total Reports: </span> 
              {result.totalReports || 0}
            </div>
            
            <div className="detail-item">
              <span className="detail-label">Last Reported: </span> 
              {formatDate(result.lastReportedAt)}
            </div>
            
            {showComments && result.reports && result.reports.length > 0 && (
              <div className="detail-item">
                <button 
                  className="btn btn-sm" 
                  onClick={toggleComments}
                >
                  {commentsVisible ? 'Hide Comments' : 'Show Comments'} ({result.reports.length})
                </button>
              </div>
            )}
          </div>
        </div>
        
        {showComments && commentsVisible && result.reports && result.reports.length > 0 && (
          <div className="comments-section">
            <h4>Report Comments</h4>
            
            {result.reports.slice(0, 10).map((report, index) => (
              <div key={index} className="comment-card">
                <div className="comment-header">
                  <span>{report.reporterCountryName || 'Unknown'} {report.reporterCountryCode ? `(${report.reporterCountryCode})` : ''}</span>
                  <span>{formatDate(report.reportedAt)}</span>
                </div>
                <div className="comment-body">
                  {report.comment || 'No comment provided'}
                </div>
              </div>
            ))}
            
            {result.reports.length > 10 && (
              <div className="more-comments">
                <em>...and {result.reports.length - 10} more reports</em>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default IPResultCard;