"""
Automation Layer - Background Report Generation Worker
Simulates cron job for automated PDF synthesis and email distribution
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from config.settings import (
    REPORT_CONFIG,
    SMTP_CONFIG,
    BASE_DIR
)
from core.database import get_database
from core.analytics import AnalyticsEngine


class ReportWorker:
    """
    Automated report generation and distribution daemon
    """
    
    def __init__(self):
        self.report_dir = REPORT_CONFIG['pdf_storage_path']
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.recipients = REPORT_CONFIG['report_recipients']
        
    def generate_weekly_report(self) -> Dict[str, any]:
        """
        Generate comprehensive weekly executive report
        
        Returns:
            Dictionary containing report metadata
        """
        
        print(f"[{datetime.now()}] Starting weekly report generation...")
        
        # Fetch data
        db = get_database()
        
        # Get last 7 days data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        data = db.fetch_recruitment_data(start_date=start_date, end_date=end_date)
        
        print(f"  → Fetched {len(data)} records for analysis")
        
        # Initialize analytics
        analytics = AnalyticsEngine(data)
        
        # Generate metrics
        kpis = analytics.calculate_executive_kpis()
        health = analytics.calculate_pipeline_health()
        client_perf = analytics.calculate_client_performance()
        dept_perf = analytics.calculate_department_performance()
        
        # Generate executive summary text
        summary_text = analytics.generate_executive_summary()
        
        # Create report metadata
        report_meta = {
            'report_id': f"WR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'generated_at': datetime.now().isoformat(),
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'total_records': len(data),
            'kpis': {
                'placements': kpis['total_placements'],
                'revenue': float(kpis['total_revenue']),
                'avg_time_to_hire': float(kpis['avg_time_to_hire']),
                'active_pipeline': kpis['active_pipeline'],
                'health_score': float(health['overall_health_score'])
            }
        }
        
        # Save text summary
        summary_path = self.report_dir / f"{report_meta['report_id']}_summary.txt"
        with open(summary_path, 'w') as f:
            f.write(summary_text)
        
        print(f"  → Summary saved to {summary_path}")
        
        # Save detailed JSON report
        json_path = self.report_dir / f"{report_meta['report_id']}_data.json"
        
        detailed_report = {
            'metadata': report_meta,
            'executive_summary': summary_text,
            'top_clients': client_perf.head(5).to_dict('records'),
            'department_performance': dept_perf.to_dict('records'),
            'pipeline_health': health
        }
        
        with open(json_path, 'w') as f:
            json.dump(detailed_report, f, indent=2, default=str)
        
        print(f"  → Detailed report saved to {json_path}")
        
        # Save CSV exports
        csv_path = self.report_dir / f"{report_meta['report_id']}_data.csv"
        data.to_csv(csv_path, index=False)
        
        print(f"  → Data export saved to {csv_path}")
        
        report_meta['files'] = {
            'summary': str(summary_path),
            'json_report': str(json_path),
            'csv_data': str(csv_path)
        }
        
        print(f"[{datetime.now()}] Report generation completed: {report_meta['report_id']}")
        
        return report_meta
    
    def send_email_report(self, report_meta: Dict[str, any]) -> bool:
        """
        Send report via email to configured recipients
        
        Args:
            report_meta: Report metadata dictionary
            
        Returns:
            Success status
        """
        
        if not REPORT_CONFIG.get('email_enabled', False):
            print("  → Email distribution disabled in config")
            return False
        
        if not SMTP_CONFIG.get('username') or not SMTP_CONFIG.get('password'):
            print("  → SMTP credentials not configured")
            return False
        
        try:
            print(f"[{datetime.now()}] Preparing email distribution...")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = SMTP_CONFIG['username']
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = f"Weekly Executive Report - {report_meta['report_id']}"
            
            # Email body
            body = f"""
Dear Executive Team,

Please find attached the weekly recruitment performance report.

REPORT SUMMARY:
- Report ID: {report_meta['report_id']}
- Period: {report_meta['period_start'][:10]} to {report_meta['period_end'][:10]}
- Total Candidates Processed: {report_meta['total_records']}

KEY METRICS:
- Placements: {report_meta['kpis']['placements']}
- Revenue: Rs. {report_meta['kpis']['revenue']:,.2f}
- Avg Time-to-Hire: {report_meta['kpis']['avg_time_to_hire']:.1f} days
- Pipeline Health Score: {report_meta['kpis']['health_score']:.1f}/100

Detailed reports are attached.

Best regards,
Gamage Recruiters Analytics System
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach files
            for file_type, file_path in report_meta['files'].items():
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
                        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                        msg.attach(part)
            
            # Send email
            with smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port']) as server:
                if SMTP_CONFIG.get('use_tls', True):
                    server.starttls()
                
                server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
                server.send_message(msg)
            
            print(f"  → Email sent successfully to {len(self.recipients)} recipients")
            return True
            
        except Exception as e:
            print(f"  → Email sending failed: {str(e)}")
            return False
    
    def run_scheduled_job(self):
        """
        Main scheduled job execution
        Simulates cron job trigger
        """
        
        print("="*70)
        print(f"WEEKLY REPORT AUTOMATION - {datetime.now()}")
        print("="*70)
        
        try:
            # Generate report
            report_meta = self.generate_weekly_report()
            
            # Send email
            if REPORT_CONFIG.get('email_enabled', False):
                self.send_email_report(report_meta)
            
            # Log execution
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'status': 'success',
                'report_id': report_meta['report_id']
            }
            
            log_path = self.report_dir / 'execution_log.jsonl'
            with open(log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            print(f"\n✓ Job completed successfully")
            print("="*70)
            
            return True
            
        except Exception as e:
            print(f"\n✗ Job failed: {str(e)}")
            
            # Log failure
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'status': 'failed',
                'error': str(e)
            }
            
            log_path = self.report_dir / 'execution_log.jsonl'
            with open(log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            print("="*70)
            return False
    
    def cleanup_old_reports(self, days_to_keep: int = 30):
        """
        Clean up reports older than specified days
        
        Args:
            days_to_keep: Number of days to retain reports
        """
        
        print(f"[{datetime.now()}] Running cleanup for reports older than {days_to_keep} days...")
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0
        
        for file_path in self.report_dir.glob('WR_*'):
            if file_path.is_file():
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_date:
                    file_path.unlink()
                    deleted_count += 1
        
        print(f"  → Deleted {deleted_count} old report files")


