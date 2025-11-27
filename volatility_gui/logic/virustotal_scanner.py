import vt
import time
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path


class VirusTotalScanner:
    """Scanner for checking file hashes against VirusTotal database."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the VirusTotal scanner.
        
        Args:
            cache_dir: Directory to store cached results
        """
        self.api_key = None
        self.client = None
        self.cache_dir = cache_dir or os.path.join(os.path.expanduser("~"), ".volatility_gui", "vt_cache")
        self.cache_file = os.path.join(self.cache_dir, "vt_cache.json")
        self.cache = {}
        
        # Rate limiting (free tier: 4 requests/minute)
        self.rate_limit = 4  # requests per minute
        self.request_times = []
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load cache
        self.load_cache()
        
    def set_api_key(self, api_key: str) -> bool:
        """
        Set and validate the VirusTotal API key.
        
        Args:
            api_key: VirusTotal API key
            
        Returns:
            True if key is valid, False otherwise
        """
        try:
            # Test the API key
            with vt.Client(api_key) as test_client:
                # Try a simple request to validate
                test_client.get_object("/files/44d88612fea8a8f36de82e1278abb02f")  # Known hash
            
            # If successful, store the key
            self.api_key = api_key
            # We don't store the client anymore to ensure thread safety
            if self.client:
                self.client.close()
                self.client = None
            return True
        except Exception as e:
            print(f"Invalid API key: {e}")
            return False

    def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limits."""
        now = time.time()
        
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        # If we've hit the rate limit, wait
        if len(self.request_times) >= self.rate_limit:
            oldest_request = min(self.request_times)
            wait_time = 60 - (now - oldest_request)
            if wait_time > 0:
                time.sleep(wait_time + 0.1)  # Add small buffer
                
        # Record this request
        self.request_times.append(time.time())

    def scan_hash(self, hash_value: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        Scan a single hash against VirusTotal.
        
        Args:
            hash_value: File hash (MD5, SHA1, or SHA256)
            force_refresh: Force API call even if cached
            
        Returns:
            Dictionary with scan results or None if error
        """
        if not self.api_key:
            return {"error": "API key not configured"}
            
        # Check cache first
        if not force_refresh and hash_value in self.cache:
            cached_result = self.cache[hash_value]
            # Check if cache is recent (less than 7 days old)
            cache_time = datetime.fromisoformat(cached_result.get("cached_at", "2000-01-01"))
            if datetime.now() - cache_time < timedelta(days=7):
                return cached_result
                
        try:
            # Wait for rate limit
            self._wait_for_rate_limit()
            
            # Query VirusTotal using a local client for thread safety
            with vt.Client(self.api_key) as client:
                file_obj = client.get_object(f"/files/{hash_value}")
                
                # Extract relevant data
                stats = file_obj.last_analysis_stats
                result = {
                    "hash": hash_value,
                    "detections": stats.get("malicious", 0) + stats.get("suspicious", 0),
                    "malicious": stats.get("malicious", 0),
                    "suspicious": stats.get("suspicious", 0),
                    "undetected": stats.get("undetected", 0),
                    "total_engines": sum(stats.values()),
                    "link": f"https://www.virustotal.com/gui/file/{hash_value}",
                    "cached_at": datetime.now().isoformat(),
                    "scan_date": file_obj.last_analysis_date.isoformat() if hasattr(file_obj, 'last_analysis_date') else None,
                    "names": file_obj.names[:5] if hasattr(file_obj, 'names') else [],  # First 5 names
                }
                
                # Cache the result
                self.cache[hash_value] = result
                self.save_cache()
                
                return result
            
        except vt.error.APIError as e:
            if e.code == "NotFoundError":
                # Hash not found in VT database
                result = {
                    "hash": hash_value,
                    "detections": 0,
                    "malicious": 0,
                    "suspicious": 0,
                    "undetected": 0,
                    "total_engines": 0,
                    "link": f"https://www.virustotal.com/gui/file/{hash_value}",
                    "cached_at": datetime.now().isoformat(),
                    "not_found": True
                }
                self.cache[hash_value] = result
                self.save_cache()
                return result
            else:
                print(f"VT API Error for {hash_value}: {e}")
                return {"error": str(e), "hash": hash_value}
        except Exception as e:
            print(f"VT Unexpected Error for {hash_value}: {e}")
            return {"error": str(e), "hash": hash_value}
            
    def scan_hashes_batch(self, hash_list: List[str], progress_callback=None) -> List[Dict[str, Any]]:
        """
        Scan multiple hashes with rate limiting.
        
        Args:
            hash_list: List of file hashes
            progress_callback: Optional callback(current, total, message)
            
        Returns:
            List of scan results
        """
        results = []
        total = len(hash_list)
        
        for i, hash_value in enumerate(hash_list):
            if progress_callback:
                progress_callback(i + 1, total, f"Scanning {hash_value[:16]}...")
                
            result = self.scan_hash(hash_value)
            if result:
                results.append(result)
                
        return results
        
    def get_cached_result(self, hash_value: str) -> Optional[Dict[str, Any]]:
        """
        Get cached result for a hash without making API call.
        
        Args:
            hash_value: File hash
            
        Returns:
            Cached result or None
        """
        return self.cache.get(hash_value)
        
    def save_cache(self):
        """Save cache to disk."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Error saving VT cache: {e}")
            
    def load_cache(self):
        """Load cache from disk."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
        except Exception as e:
            print(f"Error loading VT cache: {e}")
            self.cache = {}
            
    def clear_cache(self):
        """Clear all cached results."""
        self.cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
            
    def get_cache_stats(self) -> Dict[str, int]:
        """Get statistics about the cache."""
        return {
            "total_cached": len(self.cache),
            "malicious": sum(1 for r in self.cache.values() if r.get("malicious", 0) > 0),
            "clean": sum(1 for r in self.cache.values() if r.get("detections", 0) == 0),
        }
        
    def close(self):
        """Close the VT client connection."""
        if self.client:
            self.client.close()
