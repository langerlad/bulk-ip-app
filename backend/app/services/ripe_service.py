"""
Implementation plan for RIPE Stat API integration with IP Checker application

This module provides services for fetching and processing RIPE Stat data for IP addresses.
"""

import aiohttp
import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class RIPEStatService:
    """Service for handling RIPE Stat API operations"""
    
    BASE_URL = "https://stat.ripe.net/data"
    SOURCE_APP = "ip-checker-app"  # Register with RIPE if you make >1000 requests/day
    
    @classmethod
    async def check_ip_ripe_data(cls, ip_address, session=None):
        """
        Fetch comprehensive RIPE Stat data for an IP address
        
        Args:
            ip_address: The IP address to check
            session: Optional aiohttp session for reuse
            
        Returns:
            Dictionary with RIPE data or error
        """
        should_close_session = False
        if not session:
            session = aiohttp.ClientSession()
            should_close_session = True
            
        try:
            result = {
                'ip': ip_address,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Create tasks for all API endpoints we want to query
            tasks = [
                cls._fetch_network_info(ip_address, session),
                cls._fetch_abuse_contacts(ip_address, session),
                cls._fetch_whois_data(ip_address, session)
            ]
            
            # Run all requests concurrently
            api_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results safely
            network_info = api_results[0] if not isinstance(api_results[0], Exception) else {}
            abuse_contacts_from_api = api_results[1] if not isinstance(api_results[1], Exception) else {}
            whois_data = api_results[2] if not isinstance(api_results[2], Exception) else {}
            
            # Add results to response
            result['network_info'] = network_info
            result['abuse_contacts'] = abuse_contacts_from_api
            result['whois'] = whois_data
            
            # Extract additional information from whois data
            holder_info = cls.extract_holder_info(whois_data)
            additional_abuse_contacts = cls.extract_abuse_contacts(whois_data)
            
            # Add the extracted information directly to the result
            result['holder'] = holder_info
            
            # Merge abuse contacts from API and those extracted from WHOIS
            api_contacts = abuse_contacts_from_api.get('abuse_contacts', []) if isinstance(abuse_contacts_from_api, dict) else []
            all_contacts = list(set(api_contacts + additional_abuse_contacts))
            result['abuse_contacts'] = {'abuse_contacts': all_contacts}
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking IP {ip_address} with RIPE Stat API: {str(e)}")
            return {"error": f"Failed to fetch RIPE data: {str(e)}"}
        
        finally:
            if should_close_session:
                await session.close()
    
    @classmethod
    async def _fetch_network_info(cls, ip_address, session):
        """Fetch network info for an IP address"""
        endpoint = f"{cls.BASE_URL}/network-info/data.json"
        params = {
            'resource': ip_address,
            'sourceapp': cls.SOURCE_APP
        }
        
        try:
            async with session.get(endpoint, params=params) as response:
                if response.status != 200:
                    return {"error": f"API returned status {response.status}"}
                
                data = await response.json()
                return data.get('data', {})
                    
        except Exception as e:
            logger.error(f"Error fetching network info for {ip_address}: {str(e)}")
            return {"error": str(e)}
    
    @classmethod
    async def _fetch_abuse_contacts(cls, ip_address, session):
        """Fetch abuse contact information for an IP address"""
        endpoint = f"{cls.BASE_URL}/abuse-contact-finder/data.json"
        params = {
            'resource': ip_address,
            'sourceapp': cls.SOURCE_APP
        }
        
        try:
            async with session.get(endpoint, params=params) as response:
                if response.status != 200:
                    return {"error": f"API returned status {response.status}"}
                
                data = await response.json()
                return data.get('data', {})
                
        except Exception as e:
            logger.error(f"Error fetching abuse contacts for {ip_address}: {str(e)}")
            return {"error": str(e)}
    
    @classmethod
    async def _fetch_whois_data(cls, ip_address, session):
        """Fetch WHOIS data for an IP address"""
        endpoint = f"{cls.BASE_URL}/whois/data.json"
        params = {
            'resource': ip_address,
            'sourceapp': cls.SOURCE_APP
        }
        
        try:
            async with session.get(endpoint, params=params) as response:
                if response.status != 200:
                    return {"error": f"API returned status {response.status}"}
                
                data = await response.json()
                return data.get('data', {})
                    
        except Exception as e:
            logger.error(f"Error fetching WHOIS data for {ip_address}: {str(e)}")
            return {"error": str(e)}
    
    @classmethod
    def extract_holder_info(cls, whois_data):
        """Extract information using registry-specific approaches"""
        holder_info = {
            'name': '',
            'org': '',
            'netname': '',
            'country': '',
            'descr': '',
            'registrar': '',
            'registry': '',
            'ip_range': '',
            'cidr': '',
            'reg_date': '',
            'tech_contacts': [],
            'abuse_policy_url': ''
        }
        
        if not whois_data or not isinstance(whois_data, dict):
            return holder_info
        
        # Get the registry source
        authorities = whois_data.get('authorities', [])
        registry_source = authorities[0].lower() if isinstance(authorities, list) and authorities else ''
        holder_info['registry'] = registry_source.upper()
        
        # Get the records list
        records = whois_data.get('records', [])
        if not isinstance(records, list):
            return holder_info
        
        # Extract common fields first (valid across registries)
        for record_set in records:
            if not isinstance(record_set, list):
                continue
                
            for item in record_set:
                if not isinstance(item, dict):
                    continue
                    
                key = item.get('key', '')
                value = item.get('value', '')
                
                # Common fields
                if key == 'NetRange' or key == 'inetnum':
                    holder_info['ip_range'] = value
                elif key == 'CIDR' or key == 'route':
                    holder_info['cidr'] = value
                elif key == 'Country' or key == 'country':
                    holder_info['country'] = value
                elif key == 'NetName' or key == 'netname':
                    holder_info['netname'] = value
                elif key == 'RegDate' or key == 'created':
                    holder_info['reg_date'] = value
                elif (key == 'descr' or key == 'remarks') and not holder_info['descr']:
                    holder_info['descr'] = value
        
        # Now apply registry-specific logic for registrar info
        if registry_source == 'arin':
            # For ARIN: The registrar is in the Organization field in the 2nd record set
            # and full org name is usually in the OrgName field in the 6th record set
            if len(records) > 1:
                for item in records[1]:  # 2nd record set (0-indexed)
                    if item.get('key') == 'Organization':
                        holder_info['registrar'] = item.get('value', '')
                        if '(' in holder_info['registrar']:
                            # Extract org name without code e.g., "Google LLC (GOGL)" -> "Google LLC"
                            holder_info['registrar'] = holder_info['registrar'].split('(')[0].strip()
                        break
            
            # If no registrar yet, try the OrgName in the 6th record set
            if not holder_info['registrar'] and len(records) > 5:
                for item in records[5]:  # 6th record set
                    if item.get('key') == 'OrgName':
                        org_name = item.get('value', '')
                        # Skip if it's a registry
                        if org_name and 'Registry' not in org_name:
                            holder_info['registrar'] = org_name
                            break
        
        elif registry_source == 'ripe':
            # For RIPE: Look for org, mnt-by, or admin-c
            registrar_found = False
            
            # First try org or organisation
            for record_set in records:
                for item in record_set:
                    if item.get('key') in ['org', 'organisation']:
                        holder_info['registrar'] = item.get('value', '')
                        registrar_found = True
                        break
                if registrar_found:
                    break
            
            # If not found, try mnt-by
            if not registrar_found:
                for record_set in records:
                    for item in record_set:
                        if item.get('key') == 'mnt-by':
                            holder_info['registrar'] = item.get('value', '')
                            registrar_found = True
                            break
                    if registrar_found:
                        break
        
        elif registry_source == 'apnic':
            # For APNIC: Look for descr or mnt-by
            for record_set in records:
                for item in record_set:
                    if item.get('key') == 'descr' and not holder_info['registrar']:
                        holder_info['registrar'] = item.get('value', '')
                        break
            
            # If no registrar found in descr, try mnt-by
            if not holder_info['registrar']:
                for record_set in records:
                    for item in record_set:
                        if item.get('key') == 'mnt-by':
                            holder_info['registrar'] = item.get('value', '')
                            break
        
        elif registry_source in ['lacnic', 'afrinic']:
            # For LACNIC/AFRINIC: Look for owner or responsible
            for record_set in records:
                for item in record_set:
                    if item.get('key') in ['owner', 'responsible', 'org']:
                        holder_info['registrar'] = item.get('value', '')
                        break
        
        # If no registry-specific approach worked, use generic fallback
        if not holder_info['registrar']:
            # Collect all organization names
            org_names = []
            for record_set in records:
                for item in record_set:
                    if item.get('key') in ['OrgName', 'Organization', 'org', 'owner']:
                        org_value = item.get('value', '')
                        if org_value and 'Registry' not in org_value:
                            org_names.append(org_value)
            
            # Pick the most specific (usually shortest) non-registry org name
            if org_names:
                # Sort by length, shortest first, then take the first one
                org_names.sort(key=len)
                holder_info['registrar'] = org_names[0]
        
        # If still no registrar but we have netname, use it as a fallback
        if not holder_info['registrar'] and holder_info['netname']:
            holder_info['registrar'] = holder_info['netname']
        
        # Set primary name
        if holder_info['registrar']:
            holder_info['name'] = holder_info['registrar']
        elif holder_info['netname']:
            holder_info['name'] = holder_info['netname']
        elif holder_info['descr']:
            holder_info['name'] = holder_info['descr']
        
        return holder_info
        
    @classmethod
    def extract_abuse_contacts(cls, whois_data):
        """Extract abuse contacts from WHOIS data more thoroughly"""
        contacts = []
        
        if not whois_data or not isinstance(whois_data, dict):
            return contacts
        
        # Get the records list
        records = whois_data.get('records', [])
        if not isinstance(records, list):
            return contacts
        
        # Process each record set (which is a list)
        for record_set in records:
            if not isinstance(record_set, list):
                continue
                
            # Check each item in the record set
            for item in record_set:
                if not isinstance(item, dict):
                    continue
                
                # Look for abuse email addresses
                key = item.get('key', '')
                value = item.get('value', '')
                
                if (key == 'OrgAbuseEmail' or 
                    key == 'abuse-mailbox' or 
                    (key == 'notify' and 'abuse' in value.lower()) or 
                    ('abuse' in key.lower() and '@' in value)):
                    if value and '@' in value and value not in contacts:
                        contacts.append(value)
        
        return contacts