import re
import csv
import json
import logging
from typing import List, Dict, Any, Set, Tuple

vollog = logging.getLogger(__name__)

class IOCScanner:
    """
    Scanner for Indicators of Compromise (IOCs).
    Scans extracted forensic data for matches against a list of IOCs.
    """
    
    def __init__(self):
        self.iocs: Dict[str, Set[str]] = {
            'IP': set(),
            'Domain': set(),
            'Hash': set(),
            'Keyword': set()
        }
        
    def add_ioc(self, value: str, ioc_type: str = None):
        """
        Add a single IOC.
        
        Args:
            value: The IOC string
            ioc_type: Type of IOC (IP, Domain, Hash, Keyword). 
                      If None, attempts to auto-detect.
        """
        value = value.strip()
        if not value:
            return
            
        if not ioc_type:
            ioc_type = self._detect_type(value)
            
        if ioc_type in self.iocs:
            self.iocs[ioc_type].add(value)
            
    def remove_ioc(self, value: str, ioc_type: str):
        """Remove an IOC."""
        if ioc_type in self.iocs and value in self.iocs[ioc_type]:
            self.iocs[ioc_type].remove(value)
            
    def clear_iocs(self):
        """Clear all IOCs."""
        for key in self.iocs:
            self.iocs[key].clear()
            
    def load_from_file(self, file_path: str):
        """
        Load IOCs from a file (CSV, JSON, or TXT).
        
        Args:
            file_path: Path to the file
        """
        try:
            if file_path.lower().endswith('.json'):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Expecting dict with keys matching types or list of dicts
                    if isinstance(data, dict):
                        for key, values in data.items():
                            # Map common keys to our types
                            normalized_key = self._normalize_key(key)
                            if normalized_key:
                                for v in values:
                                    self.add_ioc(str(v), normalized_key)
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                val = item.get('value') or item.get('ioc')
                                type_ = item.get('type')
                                if val:
                                    self.add_ioc(val, type_)
                                    
            elif file_path.lower().endswith('.csv'):
                with open(file_path, 'r') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if not row:
                            continue
                        # Assume first column is value, second (optional) is type
                        val = row[0]
                        type_ = row[1] if len(row) > 1 else None
                        self.add_ioc(val, type_)
                        
            else: # TXT or other, assume one per line
                with open(file_path, 'r') as f:
                    for line in f:
                        self.add_ioc(line.strip())
                        
            vollog.info(f"Loaded IOCs from {file_path}")
            
        except Exception as e:
            vollog.error(f"Error loading IOCs from {file_path}: {e}")
            raise
            
    def scan_data(self, data: List[Dict[str, Any]], source_name: str) -> List[Dict[str, Any]]:
        """
        Scan a list of dictionaries for IOC matches.
        
        Args:
            data: List of data items (e.g., process list rows)
            source_name: Name of the source (e.g., "Process List")
            
        Returns:
            List of matches. Each match is a dict with:
            - Type: IOC type
            - Value: The matched IOC
            - Source: source_name
            - Context: String representation of the row containing the match
            - Field: The specific field where it was found
        """
        matches = []
        
        if not data:
            return matches
            
        for row in data:
            # Convert row values to string for searching
            row_str = str(row)
            
            # Check each IOC type
            for ioc_type, values in self.iocs.items():
                for ioc in values:
                    # Simple string containment check
                    # For IPs and Domains, we might want stricter checks, but containment is safer for now
                    if ioc in row_str:
                        # Find which specific field matched if possible
                        matched_field = "Unknown"
                        for k, v in row.items():
                            if ioc in str(v):
                                matched_field = k
                                break
                                
                        matches.append({
                            'Type': ioc_type,
                            'Value': ioc,
                            'Source': source_name,
                            'Context': self._get_context(row),
                            'Field': matched_field
                        })
                        
        return matches
        
    def _detect_type(self, value: str) -> str:
        """Auto-detect IOC type."""
        # IP Address (IPv4)
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', value):
            return 'IP'
            
        # Hash (MD5, SHA1, SHA256)
        if re.match(r'^[a-fA-F0-9]{32}$', value) or \
           re.match(r'^[a-fA-F0-9]{40}$', value) or \
           re.match(r'^[a-fA-F0-9]{64}$', value):
            return 'Hash'
            
        # Domain (simple check)
        if re.match(r'^[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', value):
            return 'Domain'
            
        # Default to Keyword
        return 'Keyword'
        
    def _normalize_key(self, key: str) -> str:
        """Normalize JSON keys to internal types."""
        key = key.lower()
        if 'ip' in key: return 'IP'
        if 'domain' in key or 'url' in key or 'host' in key: return 'Domain'
        if 'hash' in key or 'md5' in key or 'sha' in key: return 'Hash'
        return 'Keyword'
        
    def _get_context(self, row: Dict[str, Any]) -> str:
        """Generate a human-readable context string from a data row."""
        # Try to find identifying info like PID, Name, etc.
        parts = []
        if 'PID' in row: parts.append(f"PID: {row['PID']}")
        if 'Process' in row: parts.append(f"Process: {row['Process']}")
        if 'ImageFileName' in row: parts.append(f"Image: {row['ImageFileName']}")
        if 'Name' in row: parts.append(f"Name: {row['Name']}")
        if 'Path' in row: parts.append(f"Path: {row['Path']}")
        
        if parts:
            return ", ".join(parts)
        else:
            # Fallback to first few items
            return str(list(row.values())[:3])
