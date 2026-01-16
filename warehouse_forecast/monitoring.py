"""
Production monitoring and error notification system
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import json
from datetime import datetime


class ErrorNotifier:
    """Send alerts on critical errors"""
    
    def __init__(self, enabled=False, email_config=None):
        self.enabled = enabled
        self.email_config = email_config or {}
        self.log_file = Path("output/errors.log")
        self.log_file.parent.mkdir(exist_ok=True)
    
    def log_error(self, error_type, message, details=None):
        """Log error to file"""
        timestamp = datetime.now().isoformat()
        
        error_entry = {
            'timestamp': timestamp,
            'type': error_type,
            'message': message,
            'details': details
        }
        
        # Append to error log
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(error_entry) + '\n')
        
        logging.error(f"{error_type}: {message}")
        
        # Send email if enabled
        if self.enabled and self.email_config:
            self._send_email_alert(error_entry)
    
    def _send_email_alert(self, error_entry):
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config.get('from')
            msg['To'] = self.email_config.get('to')
            msg['Subject'] = f"[ALERT] Warehouse Forecast Error: {error_entry['type']}"
            
            body = f"""
            Warehouse Forecasting System Alert
            
            Time: {error_entry['timestamp']}
            Type: {error_entry['type']}
            Message: {error_entry['message']}
            
            Details: {error_entry. get('details', 'N/A')}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(
                self.email_config.get('smtp_server'),
                self.email_config.get('smtp_port', 587)
            )
            server.starttls()
            server.login(
                self.email_config.get('username'),
                self.email_config.get('password')
            )
            
            server.send_message(msg)
            server.quit()
            
            logging.info("Email alert sent")
            
        except Exception as e:
            logging.warning(f"Failed to send email alert: {e}")


class PerformanceMonitor:
    """Monitor system performance"""
    
    def __init__(self):
        self.metrics_file = Path("output/performance_metrics.json")
        self.metrics_file.parent.mkdir(exist_ok=True)
    
    def log_run(self, run_id, metrics):
        """Log performance metrics"""
        entry = {
            'run_id': run_id,
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics
        }
        
        # Read existing
        if self.metrics_file.exists():
            with open(self.metrics_file) as f:
                data = json.load(f)
        else:
            data = []
        
        data.append(entry)
        
        # Keep last 100 runs
        data = data[-100:]
        
        with open(self.metrics_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_average_metrics(self):
        """Get average performance metrics"""
        if not self.metrics_file.exists():
            return {}
        
        with open(self.metrics_file) as f:
            data = json.load(f)
        
        if not data:
            return {}
        
        # Calculate averages
        total_time = sum(d['metrics'].get('total_time', 0) for d in data)
        total_series = sum(d['metrics'].get('num_series', 0) for d in data)
        
        return {
            'avg_total_time': total_time / len(data),
            'avg_num_series': total_series / len(data),
            'num_runs': len(data)
        }
