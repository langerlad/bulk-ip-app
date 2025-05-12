from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify, send_file, current_app, abort
import os
import hashlib
import asyncio
import re
from app import db, limiter
from app.models.models import ApiUsage, ExportFile
from app.services.ip_service import IPService
from app.services.export_service import ExportService
from app.utils.validators import validate_api_key, is_ip_allowed

# Create blueprint
api_bp = Blueprint('api', __name__)

# Helper function to get client IP
def get_client_ip():
    """Get the client's real IP address"""
    # Try to get IP from proxy headers first (if behind reverse proxy)
    if 'X-Forwarded-For' in request.headers:
        ip = request.headers['X-Forwarded-For'].split(',')[0].strip()
    elif 'X-Real-IP' in request.headers:
        ip = request.headers['X-Real-IP']
    else:
        # Fall back to remote_addr
        ip = request.remote_addr
    
    return ip

def hash_ip(ip):
    """Create a hash of the IP for file naming without storing actual IP"""
    return hashlib.md5(ip.encode()).hexdigest()[:10]

@api_bp.before_request
def before_request():
    """Middleware to run before each request"""
    # Check API key if provided
    if 'Key' in request.headers:
        if not validate_api_key(request.headers['Key']):
            abort(403, description="Invalid API key")
    
    # Check IP whitelist if enabled
    if current_app.config.get('IP_WHITELIST'):
        client_ip = get_client_ip()
        if not is_ip_allowed(client_ip):
            abort(403, description="Your IP is not authorized to access this service")

@api_bp.route('/init', methods=['POST'])
@limiter.limit("10/minute")
def init():
    """Initialize connection and return API status"""
    client_ip = get_client_ip()
    
    # Load API usage data
    api_usage = ApiUsage.query.first()
    
    # If no data exists, create initial record
    if not api_usage:
        api_usage = ApiUsage(
            api_key=current_app.config['ABUSEIPDB_API_KEY'], 
            remaining=1000
        )
        db.session.add(api_usage)
        db.session.commit()
    else:
        # Check if we need to reset based on the date
        now = datetime.now(timezone.utc)
        if now >= api_usage.next_reset:
            api_usage.remaining_requests = 1000
            api_usage.last_reset = now
            api_usage.next_reset = api_usage.calculate_next_reset()
            db.session.commit()
    
    # Clean up old export files
    ExportService.cleanup_old_exports()
    
    return jsonify({
        'api_usage': api_usage.to_dict(),
        'client_ip': client_ip
    })

@api_bp.route('/check', methods=['POST'])
@limiter.limit("5/minute")
def check_ips():
    """Check IP addresses against AbuseIPDB"""
    data = request.json
    client_ip = get_client_ip()
    client_ip_hash = hash_ip(client_ip)
    
    # Validate request format
    if not data or 'ips' not in data:
        return jsonify({'error': 'No IP addresses provided'}), 400
    
    # Validate and clean IP list
    ip_list = IPService.validate_ip_list(data.get('ips', ''))
    
    if not ip_list['valid']:
        return jsonify({
            'error': 'No valid IP addresses found',
            'invalid_ips': ip_list['invalid']
        }), 400
        
    if ip_list['invalid']:
        # We have some invalid IPs but will proceed with the valid ones
        current_app.logger.warning(f"Invalid IPs submitted: {ip_list['invalid']}")
    
    # Get request options
    with_csv = data.get('csv', False)
    with_html = data.get('html', False)
    with_comments = data.get('comments', False)
    
    try:
        # Run the IP check using asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            IPService.check_ip_addresses(ip_list['valid'], with_comments)
        )
        loop.close()
        
        # Check for errors
        if 'error' in result:
            return jsonify({'error': result['error']}), 429
        
        # Create exports if requested
        csv_filename = None
        html_filename = None
        
        if with_csv:
            csv_filename = ExportService.create_csv_export(result['results'], client_ip_hash)
            
        if with_html:
            html_filename = ExportService.create_html_export(result['results'], client_ip_hash)
        
        # Return the results
        return jsonify({
            'data': result['results'],
            'csv_filename': csv_filename,
            'html_filename': html_filename,
            'csv': with_csv,
            'html': with_html,
            'comments': with_comments,
            'api_usage': result['api_usage'],
            'client_ip': client_ip,
            'stats': {
                'time_taken': result['time_taken'],
                'total_ips': result['total_ips'],
                'invalid_ips': len(ip_list['invalid']),
            }
        })
    
    except Exception as e:
        current_app.logger.error(f"Error in check_ips: {str(e)}")
        return jsonify({'error': f"Server error: {str(e)}"}), 500

@api_bp.route('/download/<file_type>/<filename>', methods=['GET'])
def download_export(file_type, filename):
    """Download an export file"""
    # Validate file_type
    if file_type not in ['csv', 'html']:
        abort(400, description="Invalid file type")
    
    # Sanitize filename to prevent path traversal
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    
    # Determine folder based on file type
    if file_type == 'csv':
        folder = current_app.config['CSV_FOLDER']
    else:
        folder = current_app.config['HTML_FOLDER']
    
    file_path = os.path.join(folder, filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        abort(404, description="File not found")
    
    # Verify file is in database (for security)
    export_file = ExportFile.query.filter_by(filename=filename, file_type=file_type).first()
    if not export_file:
        abort(404, description="File not found in database")
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"ip_report.{file_type}"
    )

@api_bp.route('/raw-text', methods=['POST'])
def get_raw_text():
    """Format IP addresses for display as raw text"""
    data = request.json
    
    if not data or 'ips' not in data:
        return jsonify({'error': 'No IP addresses provided'}), 400
    
    ip_addresses = data.get('ips', [])
    
    # Format IP addresses (optionally obfuscate for display)
    formatted_ips = []
    for ip in ip_addresses:
        # Replace dots with (.) and colons with (:) if needed
        if data.get('obfuscate', False):
            formatted_ip = ip.replace('.', '(.)').replace(':', '(:)')
        else:
            formatted_ip = ip
        formatted_ips.append(formatted_ip)
    
    # Join with newlines
    content = '\n'.join(formatted_ips)
    
    return jsonify({'content': content})

@api_bp.errorhandler(Exception)
def handle_error(error):
    """Global error handler for the API blueprint"""
    code = 500
    if hasattr(error, 'code'):
        code = error.code
    
    message = str(error)
    if hasattr(error, 'description'):
        message = error.description
    
    current_app.logger.error(f"API Error: {message}")
    
    return jsonify({'error': message}), code