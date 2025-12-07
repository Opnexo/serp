"""Test the UI config endpoint"""

import requests

try:
    response = requests.get("http://127.0.0.1:8000/api/ui-config")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
