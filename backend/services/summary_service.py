"""
Summary Service for Legal Document Analysis System
Manages case summaries stored as markdown files
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import hashlib

class SummaryService:
    """Service for managing case summaries"""
    
    def __init__(self, summaries_dir: str = "./summaries"):
        self.summaries_dir = Path(summaries_dir)
        self.summaries_dir.mkdir(exist_ok=True)
    
    def save_summary(self, case_id: str, summary_content: str) -> str:
        """Save a case summary to a markdown file"""
        try:
            # Create filename from case_id
            filename = f"{case_id}.md"
            file_path = self.summaries_dir / filename
            
            # Save the summary
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            
            print(f"Summary saved for case {case_id} to {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"Failed to save summary for case {case_id}: {e}")
            return ""
    
    def get_summary(self, case_id: str) -> Optional[str]:
        """Get a case summary from markdown file"""
        try:
            filename = f"{case_id}.md"
            file_path = self.summaries_dir / filename
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"Retrieved summary for case {case_id}")
                return content
            else:
                print(f"No summary file found for case {case_id}")
                return None
                
        except Exception as e:
            print(f"Failed to retrieve summary for case {case_id}: {e}")
            return None
    
    def update_summary(self, case_id: str, summary_content: str) -> bool:
        """Update an existing case summary"""
        try:
            return bool(self.save_summary(case_id, summary_content))
        except Exception as e:
            print(f"Failed to update summary for case {case_id}: {e}")
            return False
    
    def delete_summary(self, case_id: str) -> bool:
        """Delete a case summary file"""
        try:
            filename = f"{case_id}.md"
            file_path = self.summaries_dir / filename
            
            if file_path.exists():
                file_path.unlink()
                print(f"Deleted summary for case {case_id}")
                return True
            else:
                print(f"No summary file found to delete for case {case_id}")
                return False
                
        except Exception as e:
            print(f"Failed to delete summary for case {case_id}: {e}")
            return False
    
    def list_summaries(self) -> Dict[str, Dict[str, Any]]:
        """List all available case summaries with metadata"""
        summaries = {}
        
        try:
            for file_path in self.summaries_dir.glob("*.md"):
                case_id = file_path.stem
                stat = file_path.stat()
                
                summaries[case_id] = {
                    "file_path": str(file_path),
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "size_bytes": stat.st_size
                }
                
        except Exception as e:
            print(f"Failed to list summaries: {e}")
        
        return summaries
    
    def summary_exists(self, case_id: str) -> bool:
        """Check if a summary exists for the given case_id"""
        filename = f"{case_id}.md"
        file_path = self.summaries_dir / filename
        return file_path.exists()
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get statistics about stored summaries"""
        summaries = self.list_summaries()
        
        total_size = sum(s["size_bytes"] for s in summaries.values())
        
        return {
            "total_summaries": len(summaries),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "summaries_dir": str(self.summaries_dir)
        }
