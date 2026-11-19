import urllib.request
import urllib.error

def get(url):
    """Sends a GET request and prints the text content."""
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Error GET: {e}"

def status(url):
    """Checks the HTTP status code (e.g. 200, 404)."""
    try:
        with urllib.request.urlopen(url) as response:
            return response.getcode()
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        print(f"Error Status: {e}")

def ping(url):
    """Tests if a website is online (prints True or False)."""
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.getcode() == 200
    except Exception:
        return False