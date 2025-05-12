import axios from 'axios';

// Create axios instance with base URL and default config
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout for long operations
});

// Add request interceptor for adding API key
apiClient.interceptors.request.use(
  (config) => {
    // Get API key from environment or local storage if needed
    const apiKey = process.env.REACT_APP_API_KEY;
    
    if (apiKey) {
      config.headers.Key = apiKey;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

const api = {
  /**
   * Initialize connection to the API and get status
   * @returns {Promise} API response
   */
  initializeConnection: () => {
    return apiClient.post('/init');
  },
  
  /**
   * Check IP addresses against AbuseIPDB
   * @param {Object} formData - Form data with IPs and options
   * @returns {Promise} API response
   */
  checkIpAddresses: (formData) => {
    return apiClient.post('/check', formData);
  },
  
  /**
   * Download export file (CSV or HTML)
   * @param {string} fileType - File type (csv or html)
   * @param {string} filename - Name of the file to download
   * @returns {Promise} API response
   */
  downloadExport: async (fileType, filename) => {
    try {
      // Use axios directly to handle file download
      const response = await axios({
        url: `${apiClient.defaults.baseURL}/download/${fileType}/${filename}`,
        method: 'GET',
        responseType: 'blob',
        headers: apiClient.defaults.headers,
      });
      
      // Create a download link and trigger it
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `ip_report.${fileType}`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      return response;
    } catch (error) {
      console.error(`Error downloading ${fileType}:`, error);
      throw error;
    }
  },
  
  /**
   * Get raw text of IP addresses
   * @param {Array} ipAddresses - Array of IP addresses
   * @param {boolean} obfuscate - Whether to obfuscate IPs
   * @returns {Promise} API response
   */
  getRawText: (ipAddresses, obfuscate = true) => {
    return apiClient.post('/raw-text', {
      ips: ipAddresses,
      obfuscate,
    });
  },
};

export default api;