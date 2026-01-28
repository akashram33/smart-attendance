"""
Attendance Logger
Handles attendance logging and statistics
"""

import json
from pathlib import Path
from datetime import datetime
import csv

class AttendanceLogger:
    def __init__(self, logs_dir):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        self.current_date_file = None
    
    def log_attendance(self, person_name):
        """Log attendance for a person"""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.logs_dir / f"attendance_{today}.json"
        
        timestamp = datetime.now().isoformat()
        
        # Load existing logs
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # Check if person already marked attendance today
        for log in logs:
            if log['person_name'] == person_name:
                # Already marked, update check-out time
                log['checkout_time'] = timestamp
                log['duration'] = self._calculate_duration(log['timestamp'], timestamp)
        else:
            # New entry
            logs.append({
                'person_name': person_name,
                'timestamp': timestamp,
                'checkout_time': None,
                'duration': '0m'
            })
        
        # Save logs
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return timestamp
    
    def _calculate_duration(self, start, end):
        """Calculate duration between two timestamps"""
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        delta = end_dt - start_dt
        minutes = int(delta.total_seconds() / 60)
        hours = minutes // 60
        mins = minutes % 60
        
        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"
    
    def get_logs(self, date=None, person_id=None):
        """Get attendance logs"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        log_file = self.logs_dir / f"attendance_{date}.json"
        
        if not log_file.exists():
            return []
        
        with open(log_file, 'r') as f:
            logs = json.load(f)
        
        if person_id:
            logs = [l for l in logs if l.get('person_name') == person_id]
        
        return logs
    
    def get_statistics(self):
        """Get attendance statistics"""
        today = datetime.now().strftime("%Y-%m-%d")
        logs = self.get_logs(date=today)
        
        # Count unique persons present (not individual check-in/check-out records)
        unique_persons = set()
        for log in logs:
            unique_persons.add(log['person_name'])
        
        total_present = len(unique_persons)
        
        return {
            'date': today,
            'total_present': total_present,
            'total_marked': len(logs),
            'unique_persons': list(unique_persons),
            'last_updated': datetime.now().isoformat()
        }
    
    def export_to_csv(self, date=None, output_file=None):
        """Export attendance logs to CSV"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        logs = self.get_logs(date=date)
        
        if output_file is None:
            output_file = self.logs_dir / f"attendance_{date}.csv"
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['person_name', 'timestamp', 'checkout_time', 'duration'])
            writer.writeheader()
            writer.writerows(logs)
        
        return str(output_file)
