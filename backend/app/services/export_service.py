import csv
import os
import json
from datetime import datetime, timezone, timedelta
from flask import current_app, render_template
from app import db
from app.models.models import ExportFile

class ExportService:
    """Service for exporting IP check results to various formats"""
    
    @staticmethod
    def ensure_export_folders_exist():
        """Create export folders if they don't exist"""
        for folder in [
            current_app.config['EXPORT_FOLDER'],
            current_app.config['CSV_FOLDER'],
            current_app.config['HTML_FOLDER']
        ]:
            if not os.path.exists(folder):
                os.makedirs(folder)
    
    @classmethod
    def create_csv_export(cls, ip_results, ip_hash):
        """
        Create a CSV export file
        
        Args:
            ip_results: List of dictionaries containing IP check results
            ip_hash: Hash of the user's IP address for filename
            
        Returns:
            Filename of the created CSV file
        """
        cls.ensure_export_folders_exist()
        
        # Generate a unique filename
        filename = ExportFile.generate_filename(ip_hash, 'csv')
        file_path = os.path.join(current_app.config['CSV_FOLDER'], filename)
        
        # Determine the fields to include (excluding reports field to avoid large files)
        # Skip empty/None values and handle nested fields
        if not ip_results or len(ip_results) == 0:
            return None
            
        # Get all possible fields from all results
        all_fields = set()
        for result in ip_results:
            all_fields.update(result.keys())
        
        # Remove the 'reports' field which contains nested data
        if 'reports' in all_fields:
            all_fields.remove('reports')
        
        # Convert to sorted list for consistent CSV headers
        fieldnames = sorted(list(all_fields))
        
        # Write the data to CSV
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for result in ip_results:
                # Create a copy of the result excluding 'reports'
                row = {field: result.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        # Save record in the database
        export_file = ExportFile(filename, 'csv', ip_hash)
        db.session.add(export_file)
        db.session.commit()
        
        return filename
    
    @classmethod
    def create_html_export(cls, ip_results: list, ip_hash):
        """
        Create an HTML export file
        
        Args:
            ip_results: List of dictionaries containing IP check results
            ip_hash: Hash of the user's IP address for filename
            
        Returns:
            Filename of the created HTML file
        """
        cls.ensure_export_folders_exist()
        
        # Generate a unique filename
        filename = ExportFile.generate_filename(ip_hash, 'html')
        file_path = os.path.join(current_app.config['HTML_FOLDER'], filename)
        
        # Use Flask's template rendering for HTML export
        html_content = render_template(
            'export.html',
            results=ip_results,
            generated_at=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        )
        
        # Write the HTML to file with explicit UTF-8 encoding
        with open(file_path, 'w', encoding='utf-8') as htmlfile:
            htmlfile.write(html_content)
        
        # Save record in the database
        export_file = ExportFile(filename, 'html', ip_hash)
        db.session.add(export_file)
        db.session.commit()
        
        return filename
    
    @staticmethod
    def cleanup_old_exports():
        """Remove export files older than the configured expiry time"""
        cutoff_time = datetime.now(timezone.utc) - current_app.config['EXPORT_EXPIRY']
        
        # Find old export files in the database
        old_exports = ExportFile.query.filter(ExportFile.created_at < cutoff_time).all()
        
        count = 0
        for export in old_exports:
            # Determine file path based on type
            if export.file_type == 'csv':
                folder = current_app.config['CSV_FOLDER']
            else:
                folder = current_app.config['HTML_FOLDER']
                
            file_path = os.path.join(folder, export.filename)
            
            # Delete the file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
                count += 1
                
            # Remove record from database
            db.session.delete(export)
        
        db.session.commit()
        return count