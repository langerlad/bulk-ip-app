import React, { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import api from '../services/api';
import Spinner from '../components/Spinner';
import IPResultCard from '../components/IPResultCard';
import ApiStatus from '../components/ApiStatus';
import '../styles/Results.css';

const ResultsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const results = location.state?.data;
  const showComments = location.state?.showComments;
  
  // If no results data is available, redirect to the form page
  useEffect(() => {
    if (!results) {
      toast.error('No results to display. Please submit the form again.');
      navigate('/check');
    }
  }, [results, navigate]);
  
  if (!results) {
    return <Spinner message="Loading results..." />;
  }
  
  // Open raw text in a new window
  const openRawText = async () => {
    try {
      // Get all IP addresses from results
      const ipAddresses = results.data.map(item => item.ipAddress);
      
      // Call API to format IPs
      const response = await api.getRawText(ipAddresses);
      
      // Open new window with the raw text
      const rawTextWindow = window.open('/raw', '_blank');
      if (rawTextWindow) {
        // Wait for window to load then set content
        rawTextWindow.onload = () => {
          rawTextWindow.document.body.innerHTML = `<pre>${response.data.content}</pre>`;
        };
      } else {
        toast.error('Pop-up was blocked. Please allow pop-ups for this site.');
      }
    } catch (error) {
      console.error('Error generating raw text:', error);
      toast.error('Could not generate raw text');
    }
  };
  
  // Download export file
  const downloadExport = async (fileType) => {
    try {
      let filename;
      if (fileType === 'csv') {
        filename = results.csv_filename;
      } else {
        filename = results.html_filename;
      }
      
      if (!filename) {
        toast.error(`No ${fileType.toUpperCase()} file available. Please regenerate the report with ${fileType.toUpperCase()} option enabled.`);
        return;
      }
      
      // Download the file
      await api.downloadExport(fileType, filename);
      
    } catch (error) {
      console.error(`Error downloading ${fileType}:`, error);
      toast.error(`Could not download ${fileType.toUpperCase()} file. Please try again.`);
    }
  };
  
  return (
    <div className="container">
      <ApiStatus 
        apiStatus={results.api_usage} 
        clientIp={results.client_ip} 
      />
      
      <div className="results-container">
        <h1>IP Check Results</h1>
        
        <div className="stats-container">
          <div className="stat-item">
            <span className="stat-label">Checked:</span> {results.data.length} IP addresses
          </div>
          {results.stats && (
            <>
              <div className="stat-item">
                <span className="stat-label">Time:</span> {results.stats.time_taken.toFixed(2)}s
              </div>
              {results.stats.invalid_ips > 0 && (
                <div className="stat-item warning">
                  <span className="stat-label">Invalid:</span> {results.stats.invalid_ips} IPs skipped
                </div>
              )}
            </>
          )}
        </div>
        
        <div className="actions-container">
          {results.csv && (
            <button 
              className="btn btn-secondary"
              onClick={() => downloadExport('csv')}
            >
              Download CSV
            </button>
          )}
          
          {results.html && (
            <button 
              className="btn btn-secondary"
              onClick={() => downloadExport('html')}
            >
              Download HTML
            </button>
          )}
          
          <button 
            className="btn btn-secondary"
            onClick={openRawText}
          >
            View Raw IPs
          </button>
        </div>
        
        <div className="results-list">
          {results.data.map((ipResult, index) => (
            <IPResultCard 
              key={`${ipResult.ipAddress}-${index}`}
              result={ipResult}
              showComments={showComments}
            />
          ))}
        </div>
        
        {results.data.length === 0 && (
          <div className="no-results">
            <p>No results found. Please try another IP address.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsPage;