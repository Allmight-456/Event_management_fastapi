from typing import Dict, Any, List, Union
from datetime import datetime
import json

class DiffGenerator:
    """Utility class for generating detailed diffs between event versions."""
    
    @staticmethod
    def generate_detailed_diff(version1_data: Dict[str, Any], version2_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive diff showing field-by-field changes.
        This is the enhanced diff functionality highlighted in the requirements.
        """
        diff_result = {
            "summary": {
                "total_changes": 0,
                "added_fields": 0,
                "removed_fields": 0,
                "modified_fields": 0,
                "generated_at": datetime.utcnow().isoformat()
            },
            "field_changes": {},
            "structured_diff": {}
        }
        
        # Get all unique fields from both versions
        all_fields = set(version1_data.keys()) | set(version2_data.keys())
        
        for field in all_fields:
            val1 = version1_data.get(field)
            val2 = version2_data.get(field)
            
            change_info = DiffGenerator._analyze_field_change(field, val1, val2)
            
            if change_info["has_changed"]:
                diff_result["field_changes"][field] = change_info
                diff_result["summary"]["total_changes"] += 1
                
                # Update summary counters
                if change_info["change_type"] == "added":
                    diff_result["summary"]["added_fields"] += 1
                elif change_info["change_type"] == "removed":
                    diff_result["summary"]["removed_fields"] += 1
                else:
                    diff_result["summary"]["modified_fields"] += 1
        
        # Generate structured diff for complex fields
        diff_result["structured_diff"] = DiffGenerator._generate_structured_diff(version1_data, version2_data)
        
        return diff_result
    
    @staticmethod
    def _analyze_field_change(field_name: str, old_value: Any, new_value: Any) -> Dict[str, Any]:
        """Analyze changes in a specific field."""
        change_info = {
            "field": field_name,
            "has_changed": old_value != new_value,
            "change_type": "unchanged",
            "old_value": old_value,
            "new_value": new_value,
            "old_value_type": type(old_value).__name__ if old_value is not None else "null",
            "new_value_type": type(new_value).__name__ if new_value is not None else "null",
            "human_readable": ""
        }
        
        if not change_info["has_changed"]:
            return change_info
        
        # Determine change type
        if old_value is None and new_value is not None:
            change_info["change_type"] = "added"
            change_info["human_readable"] = f"Added {field_name}: {new_value}"
        elif old_value is not None and new_value is None:
            change_info["change_type"] = "removed"
            change_info["human_readable"] = f"Removed {field_name}: {old_value}"
        else:
            change_info["change_type"] = "modified"
            change_info["human_readable"] = f"Changed {field_name}: {old_value} → {new_value}"
        
        # Special handling for datetime fields
        if field_name in ["start_time", "end_time", "created_at", "updated_at"]:
            change_info["datetime_diff"] = DiffGenerator._analyze_datetime_change(old_value, new_value)
        
        # Special handling for JSON fields
        if field_name == "recurrence_pattern" and isinstance(old_value, dict) and isinstance(new_value, dict):
            change_info["json_diff"] = DiffGenerator._analyze_json_change(old_value, new_value)
        
        return change_info
    
    @staticmethod
    def _analyze_datetime_change(old_dt: Any, new_dt: Any) -> Dict[str, Any]:
        """Analyze changes in datetime fields."""
        if not isinstance(old_dt, datetime) or not isinstance(new_dt, datetime):
            return {"error": "Invalid datetime values"}
        
        time_diff = new_dt - old_dt
        
        return {
            "old_datetime": old_dt.isoformat(),
            "new_datetime": new_dt.isoformat(),
            "time_difference_seconds": time_diff.total_seconds(),
            "time_difference_human": DiffGenerator._humanize_time_diff(time_diff.total_seconds()),
            "moved_earlier": time_diff.total_seconds() < 0,
            "moved_later": time_diff.total_seconds() > 0
        }
    
    @staticmethod
    def _analyze_json_change(old_json: Dict[str, Any], new_json: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze changes in JSON fields like recurrence patterns."""
        json_diff = {
            "added_keys": [],
            "removed_keys": [],
            "modified_keys": {},
            "unchanged_keys": []
        }
        
        old_keys = set(old_json.keys())
        new_keys = set(new_json.keys())
        
        json_diff["added_keys"] = list(new_keys - old_keys)
        json_diff["removed_keys"] = list(old_keys - new_keys)
        
        common_keys = old_keys & new_keys
        for key in common_keys:
            if old_json[key] != new_json[key]:
                json_diff["modified_keys"][key] = {
                    "old": old_json[key],
                    "new": new_json[key]
                }
            else:
                json_diff["unchanged_keys"].append(key)
        
        return json_diff
    
    @staticmethod
    def _generate_structured_diff(data1: Dict[str, Any], data2: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a Git-style structured diff."""
        structured = {
            "additions": {},
            "deletions": {},
            "modifications": {}
        }
        
        all_keys = set(data1.keys()) | set(data2.keys())
        
        for key in all_keys:
            if key not in data1:
                structured["additions"][key] = data2[key]
            elif key not in data2:
                structured["deletions"][key] = data1[key]
            elif data1[key] != data2[key]:
                structured["modifications"][key] = {
                    "before": data1[key],
                    "after": data2[key]
                }
        
        return structured
    
    @staticmethod
    def _humanize_time_diff(seconds: float) -> str:
        """Convert seconds to human-readable time difference."""
        abs_seconds = abs(seconds)
        
        if abs_seconds < 60:
            return f"{int(abs_seconds)} seconds"
        elif abs_seconds < 3600:
            return f"{int(abs_seconds // 60)} minutes"
        elif abs_seconds < 86400:
            return f"{int(abs_seconds // 3600)} hours"
        else:
            return f"{int(abs_seconds // 86400)} days"
    
    @staticmethod
    def generate_text_diff(version1_data: Dict[str, Any], version2_data: Dict[str, Any]) -> str:
        """Generate a text-based diff similar to Git diff format."""
        lines = ["--- Version 1", "+++ Version 2"]
        
        all_keys = sorted(set(version1_data.keys()) | set(version2_data.keys()))
        
        for key in all_keys:
            val1 = version1_data.get(key)
            val2 = version2_data.get(key)
            
            if val1 != val2:
                if key not in version1_data:
                    lines.append(f"+{key}: {val2}")
                elif key not in version2_data:
                    lines.append(f"-{key}: {val1}")
                else:
                    lines.append(f"-{key}: {val1}")
                    lines.append(f"+{key}: {val2}")
        
        return "\n".join(lines)
