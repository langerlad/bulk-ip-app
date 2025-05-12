import aiohttp
import asyncio
import ipaddress
import re
from datetime import datetime, timezone, timedelta
from flask import current_app
from app import db
from app.models.models import ApiUsage, IPCheckResult

class IPService:
    """Service for handling IP address operations and AbuseIPDB API interactions"""
    
    @staticmethod
    def validate_ip_list(ip_list_text):
        """
        Validate a list of IP addresses from user input
        Returns a dictionary with valid and invalid IPs
        """
        # Clean input and split by lines
        clean_text = re.sub(r'[^\da-zA-Z.:\n]', '', ip_list_text)
        ip_list = [ip.strip() for ip in clean_text.splitlines() if ip.strip()]
        
        result = {"valid": [], "invalid": []}
        
        for ip in ip_list:
            try:
                # Validate IP address format (both IPv4 and IPv6)
                ipaddress.ip_address(ip)
                result["valid"].append(ip)
            except ValueError:
                result["invalid"].append(ip)
                
        return result
    
    @staticmethod
    async def check_single_ip(ip_address, session, with_comments=False):
        """Check a single IP against AbuseIPDB API"""
        # First check if we have a recent result in the database
        cached_result = IPCheckResult.get_recent(ip_address)
        if cached_result:
            current_app.logger.info(f"Using cached result for {ip_address}")
            return cached_result
        
        # Set up the API request
        api_key = current_app.config['ABUSEIPDB_API_KEY']
        max_age = current_app.config['ABUSEIPDB_MAX_AGE_DAYS']
        
        url = f"{current_app.config['ABUSEIPDB_API_URL']}/check"
        
        # Always request verbose to get all available information
        params = {
            'ipAddress': ip_address,
            'maxAgeInDays': max_age,
            'verbose': ''  # Include verbose data in all requests
        }
        
        headers = {
            'Accept': 'application/json',
            'Key': api_key
        }
        
        # Make the API request
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    error_data = await response.json()
                    return {"error": error_data.get('errors', [{'detail': 'API request failed'}])[0]['detail']}
                
                data = await response.json()
                result = data.get('data', {})
                
                # Store in database for caching
                db_result = IPCheckResult(ip_address, result)
                db.session.add(db_result)
                db.session.commit()
                
                return result
            
        except Exception as e:
            current_app.logger.error(f"Error checking IP {ip_address}: {str(e)}")
            return {"error": f"Failed to check IP: {str(e)}"}
    
    @classmethod
    async def check_ip_addresses(cls, ip_list, with_comments=False):
        """
        Check multiple IP addresses against AbuseIPDB API in parallel
        """
        api_usage = ApiUsage.query.first()
        
        # Make sure we have enough API requests left
        if api_usage and api_usage.remaining_requests < len(ip_list):
            return {"error": f"Insufficient API requests remaining. You have {api_usage.remaining_requests} left but need {len(ip_list)}."}
        
        # Start timing the operation
        start_time = datetime.now(timezone.utc)
        
        # Create aiohttp session for async requests
        async with aiohttp.ClientSession() as session:
            # Create tasks for each IP address
            tasks = [cls.check_single_ip(ip, session, with_comments) for ip in ip_list]
            
            # Run all tasks concurrently and gather results
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle any exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    current_app.logger.error(f"Error checking IP {ip_list[i]}: {str(result)}")
                    processed_results.append({
                        "ipAddress": ip_list[i],
                        "error": str(result)
                    })
                elif isinstance(result, dict) and "error" in result:
                    processed_results.append({
                        "ipAddress": ip_list[i],
                        "error": result["error"]
                    })
                else:
                    processed_results.append(result)
        
        # Update API usage
        if api_usage:
            api_usage.use_request(len(ip_list))
            
        # Calculate total time taken
        time_taken = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        return {
            "results": processed_results,
            "time_taken": time_taken,
            "total_ips": len(ip_list),
            "api_usage": api_usage.to_dict() if api_usage else None
        }