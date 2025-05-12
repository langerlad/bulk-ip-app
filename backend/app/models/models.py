from app import db
from datetime import datetime, timezone, timedelta
from sqlalchemy.types import TypeDecorator, DateTime
import uuid
import json

class TZDateTime(TypeDecorator):
    """Converts UTC datetime from/to timezone-aware datetime."""
    impl = DateTime
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
        
    def process_result_value(self, value, dialect):
        if value is not None:
            return value.replace(tzinfo=timezone.utc)
        return value

class ApiUsage(db.Model):
    """Tracks API usage statistics and limits"""
    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(100), unique=True, nullable=False)
    total_requests = db.Column(db.Integer, default=0)
    remaining_requests = db.Column(db.Integer, default=1000)
    last_request = db.Column(TZDateTime, default=lambda: datetime.now(timezone.utc))
    last_reset = db.Column(TZDateTime, default=lambda: datetime.now(timezone.utc))
    next_reset = db.Column(TZDateTime)
    
    def __init__(self, api_key, remaining=1000):
        self.api_key = api_key
        self.remaining_requests = remaining
        self.last_reset = datetime.now(timezone.utc)
        self.next_reset = self.calculate_next_reset()

    def calculate_next_reset(self):
        """Calculate when the API limit resets (midnight UTC)"""
        now = datetime.now(timezone.utc)
        tomorrow = now + timedelta(days=1)
        # Set to midnight UTC of the next day
        return datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0, tzinfo=timezone.utc)
    
    def use_request(self, count=1):
        """Records usage of API requests"""
        # Check if we need to reset counters first
        now = datetime.now(timezone.utc)
        if now >= self.next_reset:
            self.remaining_requests = 1000
            self.last_reset = now
            self.next_reset = self.calculate_next_reset()
        
        # Then update counters
        self.total_requests += count
        self.remaining_requests -= count
        self.last_request = now
        
        db.session.commit()
        
    def to_dict(self):
        return {
            'remaining_requests': self.remaining_requests,
            'total_limit': 1000,  # Daily limit from AbuseIPDB
            'next_reset': self.next_reset.isoformat() if self.next_reset else None,
            'last_reset': self.last_reset.isoformat() if self.last_reset else None
        }


class ExportFile(db.Model):
    """Keeps track of exported files for cleanup"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # 'csv' or 'html'
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    ip_hash = db.Column(db.String(100), nullable=False)  # Hash of user's IP
    
    def __init__(self, filename, file_type, ip_hash):
        self.filename = filename
        self.file_type = file_type
        self.ip_hash = ip_hash
    
    @classmethod
    def generate_filename(cls, ip_hash, file_type):
        """Generate a unique filename for exports"""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4()).replace('-', '')[:10]
        return f"{ip_hash}_{timestamp}_{unique_id}.{file_type}"


class IPCheckResult(db.Model):
    """Stores IP check results for caching and history"""
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False, index=True)
    last_checked = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    response_data = db.Column(db.Text, nullable=False)
    
    def __init__(self, ip_address, response_data):
        self.ip_address = ip_address
        self.response_data = json.dumps(response_data)
    
    def get_data(self):
        """Returns the response data as a dictionary"""
        return json.loads(self.response_data)
    
    @classmethod
    def get_recent(cls, ip_address, max_age_minutes=10):
        """Get recent result if available"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=max_age_minutes)
        result = cls.query.filter(
            cls.ip_address == ip_address,
            cls.last_checked >= cutoff_time
        ).order_by(cls.last_checked.desc()).first()
        
        if result:
            return result.get_data()
        return None