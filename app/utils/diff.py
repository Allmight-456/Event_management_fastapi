from typing import Dict, Any, List
from datetime import datetime
import json

class DiffGenerator:
    """Utility class for generating diffs between versions."""
    
    @staticmethod
    def generate_detailed_diff(version1_data: Dict[str, Any], version2_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed diff between two versions."""
        diff = {
            "summary": {
                "total_changes": 0,
                "added_fields": 0,
                "removed_fields": 0,
                "modified_fields": 0
            },
            "field_changes": {}
        }
        
        all_fields = set(version1_data.keys()) | set(version2_data.keys())
        
        for field in all_fields:
            val1 = version1_data.get(field)
            val2 = version2_data.get(field)
            
            if val1 != val2:
                diff["summary"]["total_changes"] += 1
                
                if val1 is None:
                    diff["summary"]["added_fields"] += 1
                    change_type = "added"
                elif val2 is None:
                    diff["summary"]["removed_fields"] += 1
                    change_type = "removed"
                else:
                    diff["summary"]["modified_fields"] += 1
                    change_type = "modified"
                
                diff["field_changes"][field] = {
                    "old_value": str(val1) if val1 is not None else None,
                    "new_value": str(val2) if val2 is not None else None,
                    "change_type": change_type
                }
        
        return diff
    
    @staticmethod
    def generate_text_diff(version1_data: Dict[str, Any], version2_data: Dict[str, Any]) -> str:
        """Generate text-based diff."""
        lines = ["--- Version 1", "+++ Version 2"]
        
        all_fields = set(version1_data.keys()) | set(version2_data.keys())
        
        for field in sorted(all_fields):
            val1 = version1_data.get(field)
            val2 = version2_data.get(field)
            
            if val1 != val2:
                if val1 is not None:
                    lines.append(f"-{field}: {val1}")
                if val2 is not None:
                    lines.append(f"+{field}: {val2}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _humanize_time_diff(seconds: int) -> str:
        """Convert seconds to human readable format."""
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            return f"{seconds // 60} minutes"
        elif seconds < 86400:
            return f"{seconds // 3600} hours"
        else:
            return f"{seconds // 86400} days"
