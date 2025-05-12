import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import api from '../services/api';
import Spinner from '../components/Spinner';
import ApiStatus from '../components/ApiStatus';
import '../styles/IPForm.css';

const IPFormPage = () => {
  const [formData, setFormData] = useState({
    ips: '',
    csv: false,
    html: false,
    comments: false
  });
  
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState(null);
  const [clientIp, setClientIp] = useState('');
  const navigate = useNavigate();
  
  // On component mount, initialize and get API status
  useEffect(() => {
    const initializeApp = async () => {
      try {
        setLoading(true);
        
        // Try to get saved IPs from localStorage
        const savedIps = localStorage.getItem('ip_checker_ips');
        if (savedIps) {
          setFormData(prev => ({
            ...prev,
            ips: savedIps
          }));
        }
        
        // Initialize API connection
        const response = await api.initializeConnection();
        console.log('API Status Response:', response.data);
        
        setApiStatus(response.data.api_usage);
        setClientIp(response.data.client_ip);
        
      } catch (error) {
        console.error('Error initializing app:', error);
        const errorMsg = error.response?.data?.error || 'Could not connect to the server';
        toast.error(errorMsg);
        navigate('/error', { state: { errorMessage: errorMsg } });
      } finally {
        setLoading(false);
      }
    };
    
    initializeApp();
    
    // Clear localStorage on browser close
    window.addEventListener('beforeunload', () => {
      localStorage.removeItem('ip_checker_ips');
    });
    
  }, [navigate]);
  
  // Handle form input changes
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Save IPs to localStorage for persistence
    if (name === 'ips') {
      localStorage.setItem('ip_checker_ips', value);
    }
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.ips.trim()) {
      toast.error('Please enter at least one IP address');
      return;
    }
    
    try {
      setLoading(true);
      
      const response = await api.checkIpAddresses(formData);
      
      navigate('/results', { 
        state: { 
          data: response.data,
          showComments: formData.comments
        } 
      });
      
    } catch (error) {
      console.error('Error checking IPs:', error);
      const errorMsg = error.response?.data?.error || 'An error occurred while processing your request';
      toast.error(errorMsg);
      
      if (error.response?.status === 400 && error.response.data?.invalid_ips) {
        // Show specific error for invalid IPs
        navigate('/error', { 
          state: { 
            errorMessage: 'Some IP addresses are invalid',
            invalidIps: error.response.data.invalid_ips
          } 
        });
      } else {
        navigate('/error', { state: { errorMessage: errorMsg } });
      }
    } finally {
      setLoading(false);
    }
  };
  
  if (loading && !apiStatus) {
    return <Spinner message="Initializing application..." />;
  }
  
  return (
    <div className="container">
      {apiStatus && (
      <div className="api-usage-banner">
        <h3>AbuseIPDB API Usage</h3>
        <div className="usage-info">
          <p><strong>Remaining Requests:</strong> {apiStatus.remaining_requests} out of 1000</p>
          <p><strong>Reset Time:</strong> {new Date(apiStatus.next_reset).toLocaleString()}</p>
        </div>
      </div>
      )}

      <ApiStatus apiStatus={apiStatus} clientIp={clientIp} />
      
      {loading ? (
        <div className="loading-container">
          <Spinner message="Processing IP addresses..." />
        </div>
      ) : (
        <div className="form-container">
          <h1>IP Address Checker</h1>
          <p className="form-description">
            Enter IP addresses (one per line) to check against AbuseIPDB database.
          </p>
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <textarea
                className="form-control"
                name="ips"
                rows="12"
                placeholder="Enter IP addresses here (one per line)"
                value={formData.ips}
                onChange={handleChange}
                required
              />
            </div>
            
            <div className="form-options">
              <div className="option-group">
                <h3>Export Options</h3>
                <div className="checkbox-label">
                  <input
                    type="checkbox"
                    name="csv"
                    id="csv"
                    checked={formData.csv}
                    onChange={handleChange}
                  />
                  <label htmlFor="csv">Export to CSV</label>
                </div>
                
                <div className="checkbox-label">
                  <input
                    type="checkbox"
                    name="html"
                    id="html"
                    checked={formData.html}
                    onChange={handleChange}
                  />
                  <label htmlFor="html">Export to HTML</label>
                </div>
              </div>
              
              <div className="option-group">
                <h3>Content Options</h3>
                <div className="checkbox-label">
                  <input
                    type="checkbox"
                    name="comments"
                    id="comments"
                    checked={formData.comments}
                    onChange={handleChange}
                  />
                  <label htmlFor="comments">Include report comments</label>
                </div>
              </div>
            </div>
            
            <button type="submit" className="btn btn-primary">
              Check IP Addresses
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default IPFormPage;