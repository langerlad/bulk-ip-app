# IP Checker Application

A modern web application to check IP addresses against the AbuseIPDB database, providing detailed information about potentially malicious IP addresses.

## Features

- **IP Address Checking**: Check multiple IP addresses simultaneously against the AbuseIPDB database
- **Detailed Reports**: View comprehensive information for each IP address including abuse confidence score, location, ISP, and more
- **Comments/Reports**: View user-submitted comments and reports for flagged IP addresses
- **Export Options**: Export results in CSV or HTML formats for offline analysis or sharing
- **Raw Text Export**: Get a clean list of IP addresses for easy copying
- **API Usage Tracking**: Monitor your AbuseIPDB API usage limits and reset times
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Project Structure

The application consists of a Flask backend API and a React frontend:

### Backend (Flask)

- RESTful API built with Flask
- PostgreSQL database for tracking API usage and exports
- Async processing with aiohttp for optimal performance
- Secure file handling and sanitization to prevent common vulnerabilities
- API rate limiting to prevent abuse

### Frontend (React)

- Modern React with hooks and React Router
- Clean, responsive UI
- Real-time API status monitoring
- User-friendly IP entry and results display
- Export functionality with downloadable files
- Interactive report comments display

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- PostgreSQL (optional, SQLite can be used for development)
- AbuseIPDB API key (sign up at [AbuseIPDB](https://www.abuseipdb.com/))

### Backend Setup

1. Clone this repository
2. Navigate to the backend directory
3. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Create a `.env` file with the following variables:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   FLASK_DEBUG=true
   SECRET_KEY=your-secret-key-here
   ABUSEIPDB_API_KEY=your-abuseipdb-api-key
   FLASK_KEY=your-app-api-key
   DATABASE_URL=postgresql://username:password@localhost/ip_checker
   CORS_ORIGIN=http://localhost:3000
   IP_WHITELIST=127.0.0.1,192.168.1.0/24  # Optional IP whitelist
   ```
6. Create necessary directories:
   ```
   mkdir -p reports/csv reports/html
   ```
7. Initialize the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```
8. Run the application:
   ```
   flask run
   ```

### Frontend Setup

1. Navigate to the frontend directory
2. Install dependencies:
   ```
   npm install
   ```
3. Create a `.env` file with:
   ```
   REACT_APP_API_URL=http://localhost:5000/api
   REACT_APP_API_KEY=your-app-api-key  # Same as FLASK_KEY in backend
   ```
4. Start the development server:
   ```
   npm start
   ```
5. The application will be available at `http://localhost:3000`

## Production Deployment

### Backend

1. Set the environment variables appropriately for production:
   ```
   FLASK_ENV=production
   FLASK_DEBUG=false
   ```
2. Use a production WSGI server like Gunicorn:
   ```
   gunicorn --workers=4 --bind=0.0.0.0:5000 "app:create_app()"
   ```
3. Consider using a reverse proxy like Nginx for SSL termination and request forwarding

### Frontend

1. Build the production version:
   ```
   npm run build
   ```
2. Serve the static files using Nginx or another web server

## API Documentation

### Endpoints

- `POST /api/init` - Initialize connection and get API status
- `POST /api/check` - Check IP addresses
- `GET /api/download/{file_type}/{filename}` - Download an export file
- `POST /api/raw-text` - Format IP addresses for display as raw text

### Request/Response Examples

#### Check IP Addresses

Request:
```json
{
  "ips": "192.168.1.1\n8.8.8.8\n1.1.1.1",
  "csv": true,
  "html": false,
  "comments": true
}
```

Response:
```json
{
  "data": [
    {
      "ipAddress": "192.168.1.1",
      "abuseConfidenceScore": 0,
      "countryCode": "US",
      "countryName": "United States",
      "isp": "Private",
      "domain": "",
      "usageType": "Private",
      "hostnames": [],
      "totalReports": 0,
      "lastReportedAt": null
    },
    // More IP results...
  ],
  "csv_filename": "abc123_20240505_xyz789.csv",
  "html_filename": null,
  "csv": true,
  "html": false,
  "comments": true,
  "api_usage": {
    "remaining_requests": 987,
    "next_reset": "2024-05-06T00:00:00Z",
    "last_reset": "2024-05-05T00:00:00Z"
  },
  "client_ip": "127.0.0.1",
  "stats": {
    "time_taken": 1.234,
    "total_ips": 3,
    "invalid_ips": 0
  }
}
```

## Security Considerations

- API keys are protected and not exposed to clients
- IP addresses are hashed for file naming to preserve privacy
- Path traversal prevention for file downloads
- Rate limiting to prevent abuse
- Input sanitization to prevent injection attacks
- CORS protections for API endpoints
- Optional IP whitelist for restricted access

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [AbuseIPDB](https://www.abuseipdb.com/) for providing the API
- [Flask](https://flask.palletsprojects.com/) for the backend framework
- [React](https://reactjs.org/) for the frontend framework