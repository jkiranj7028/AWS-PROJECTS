import time
import requests

url = 'http://localhost:8080/health'
def check_service_availability(url):
    """Continuously checks if a service at a given URL is available."""
    while True:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"[{time.ctime()}] Service at {url} is UP (Status: {response.status_code})")
            else:
                print(f"[{time.ctime()}] Service at {url} is DOWN (Status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"[{time.ctime()}] Service at {url} is DOWN (Error: {e})")
        time.sleep(10)  # Check every 10 seconds

# Example usage:
# check_service_availability("http://localhost:8080/health")
