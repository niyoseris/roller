"""
Session Manager for Agentic Trend Collector
Manages scan sessions, progress tracking, and report storage
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

SESSION_FILE = "scan_session.json"
REPORTS_FILE = "scan_reports.json"


class SessionManager:
    """Manages scan sessions and progress tracking"""
    
    def __init__(self):
        self.session = self.load_session()
        self.reports = self.load_reports()
    
    def load_session(self) -> Dict:
        """Load session from file"""
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading session: {e}")
        
        return {
            "manual_trends": [],
            "trend_data": {},  # Maps trend -> {url, category} from Gemini
            "current_index": 0,
            "processed_trends": [],
            "failed_trends": [],
            "status": "idle",  # idle, running, paused, completed
            "created_at": None,
            "updated_at": None,
            "total_trends": 0,
            "successful": 0,
            "failed": 0
        }
    
    def save_session(self):
        """Save session to file"""
        try:
            self.session['updated_at'] = datetime.now().isoformat()
            with open(SESSION_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.session, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving session: {e}")
    
    def load_reports(self) -> Dict:
        """Load reports from file"""
        if os.path.exists(REPORTS_FILE):
            try:
                with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading reports: {e}")
        return {}
    
    def save_reports(self):
        """Save reports to file"""
        try:
            with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.reports, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving reports: {e}")
    
    def start_new_session(self, trends: List[str], trend_data: Dict[str, Dict] = None, auto_start: bool = False) -> bool:
        """Start a new scan session with manual trends
        
        Args:
            trends: List of trend names
            trend_data: Optional dict mapping trend -> {url, category} from Gemini
            auto_start: If True, status will be "running", otherwise "paused"
        """
        if not trends:
            return False
        
        self.session = {
            "manual_trends": trends,
            "trend_data": trend_data or {},
            "current_index": 0,
            "processed_trends": [],
            "failed_trends": [],
            "status": "running" if auto_start else "paused",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "total_trends": len(trends),
            "successful": 0,
            "failed": 0
        }
        self.save_session()
        return True
    
    def add_trends_to_session(self, trends: List[str]) -> bool:
        """Add new trends to existing session"""
        if not trends:
            return False
        
        # Add only unique trends
        for trend in trends:
            if trend not in self.session['manual_trends']:
                self.session['manual_trends'].append(trend)
        
        self.session['total_trends'] = len(self.session['manual_trends'])
        self.session['updated_at'] = datetime.now().isoformat()
        self.save_session()
        return True
    
    def get_next_trend(self) -> Optional[str]:
        """Get next trend to process"""
        if self.session['status'] != 'running':
            return None
        
        if self.session['current_index'] >= len(self.session['manual_trends']):
            self.complete_session()
            return None
        
        trend = self.session['manual_trends'][self.session['current_index']]
        return trend
    
    def get_trend_data(self, trend: str) -> Optional[Dict]:
        """Get trend data (URL + category) from Gemini if available"""
        return self.session.get('trend_data', {}).get(trend)
    
    def get_wikipedia_url(self, trend: str) -> Optional[str]:
        """Get Wikipedia URL for a trend (from Gemini if available)"""
        trend_data = self.get_trend_data(trend)
        if trend_data and isinstance(trend_data, dict):
            return trend_data.get('url')
        elif isinstance(trend_data, str):
            # Backward compatibility: old format was just URL string
            return trend_data
        return None
    
    def get_category(self, trend: str) -> Optional[str]:
        """Get category for a trend (from Gemini if available)"""
        trend_data = self.get_trend_data(trend)
        if trend_data and isinstance(trend_data, dict):
            return trend_data.get('category')
        return None
    
    def mark_trend_processed(self, trend: str, success: bool, report: Dict):
        """Mark a trend as processed"""
        self.session['current_index'] += 1
        
        if success:
            self.session['processed_trends'].append(trend)
            self.session['successful'] += 1
            
            # Save report
            self.reports[trend] = {
                **report,
                'processed_at': datetime.now().isoformat(),
                'success': True
            }
        else:
            self.session['failed_trends'].append(trend)
            self.session['failed'] += 1
            
            # Save failure info
            self.reports[trend] = {
                **report,
                'processed_at': datetime.now().isoformat(),
                'success': False
            }
        
        self.save_session()
        self.save_reports()
    
    def pause_session(self):
        """Pause current session"""
        self.session['status'] = 'paused'
        self.save_session()
    
    def resume_session(self):
        """Resume paused session"""
        if self.session['status'] == 'paused':
            self.session['status'] = 'running'
            self.save_session()
            return True
        return False
    
    def complete_session(self):
        """Mark session as completed"""
        self.session['status'] = 'completed'
        self.save_session()
    
    def reset_session(self, clear_url_tracker=True):
        """Reset session to start over and optionally clear all processed URLs
        
        Args:
            clear_url_tracker: If True, also clears all processed URLs from url_tracker
        """
        self.session = {
            "manual_trends": [],
            "trend_data": {},
            "current_index": 0,
            "processed_trends": [],
            "failed_trends": [],
            "status": "idle",
            "created_at": None,
            "updated_at": None,
            "total_trends": 0,
            "successful": 0,
            "failed": 0
        }
        self.reports = {}  # Also clear reports
        self.save_session()
        self.save_reports()
        
        # Clear URL tracker to allow reprocessing all trends
        if clear_url_tracker:
            from url_tracker import URLTracker
            url_tracker = URLTracker()
            url_tracker.clear()
            logger.info("🗑️  Cleared all processed URLs - all trends can be processed again")
    
    def get_session_status(self) -> Dict:
        """Get current session status"""
        return {
            "status": self.session['status'],
            "total_trends": self.session['total_trends'],
            "current_index": self.session['current_index'],
            "successful": self.session['successful'],
            "failed": self.session['failed'],
            "progress_percentage": (self.session['current_index'] / self.session['total_trends'] * 100) 
                                   if self.session['total_trends'] > 0 else 0,
            "created_at": self.session['created_at'],
            "updated_at": self.session['updated_at']
        }
    
    def get_reports(self) -> Dict:
        """Get all reports"""
        return self.reports
    
    def get_report(self, trend: str) -> Optional[Dict]:
        """Get report for a specific trend"""
        return self.reports.get(trend)
    
    def clear_reports(self):
        """Clear all reports"""
        self.reports = {}
        self.save_reports()
