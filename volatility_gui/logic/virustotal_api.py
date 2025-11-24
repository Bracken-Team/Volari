import requests
import logging

vollog = logging.getLogger(__name__)

class VirusTotalAPI:
    BASE_URL = "https://www.virustotal.com/api/v3"

    def __init__(self, api_key=None):
        self.api_key = api_key

    def set_api_key(self, api_key):
        self.api_key = api_key

    def scan_file_hash(self, file_hash):
        if not self.api_key:
            raise ValueError("API Key is not set")

        url = f"{self.BASE_URL}/files/{file_hash}"
        headers = {
            "x-apikey": self.api_key
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            vollog.error(f"VirusTotal API Error: {e}")
            if response.status_code == 404:
                return {"error": "Hash not found in VirusTotal"}
            raise e

    def scan_ip(self, ip_address):
        if not self.api_key:
            raise ValueError("API Key is not set")

        url = f"{self.BASE_URL}/ip_addresses/{ip_address}"
        headers = {
            "x-apikey": self.api_key
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            vollog.error(f"VirusTotal API Error: {e}")
            raise e
