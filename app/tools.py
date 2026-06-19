import whois
import requests
from playwright.sync_api import sync_playwright
import os

def run_whois(domain_or_ip):
    """Runs a WHOIS lookup on a domain or IP."""
    try:
        w = whois.whois(domain_or_ip)
        return dict(w)
    except Exception as e:
        return {"error": str(e)}

def run_reverse_image_search(image_path_or_url):
    """Attempts a reverse image search using Playwright (Google Lens)."""
    # Note: Google Lens often blocks headless browsers. This is a best-effort approach.
    # A robust solution might just return the URL for manual inspection.
    results = {"status": "Attempted", "details": "Automated reverse image search is highly unreliable due to CAPTCHAs. Consider manual search.", "manual_link": "https://images.google.com/"}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # This is a placeholder for actual interaction, which is complex for Google Lens upload
            # A more realistic approach for an automated agent is to upload to an API if available,
            # or rely on the user manually following a link.
            # page.goto("https://images.google.com/")
            # ... interaction logic ...
            browser.close()
    except Exception as e:
         results["error"] = str(e)
    return results

def check_email_breach(email):
    """Checks HIBP for email breaches (basic check without API key)."""
    # Note: HIBP requires an API key for full email breach searches.
    # If no key is provided, we can only provide a link to manual search.
    api_key = os.getenv("HIBP_API_KEY")
    if not api_key:
        return {"status": "Manual check required", "link": f"https://haveibeenpwned.com/account/{email}"}
    
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {
        "hibp-api-key": api_key,
        "user-agent": "OSINT-Agent-Docker"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"status": "No breaches found."}
        else:
            return {"error": f"API returned status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def generate_map_links(lat, lon):
    """Generates useful map links from coordinates."""
    if not lat or not lon:
        return {}
    return {
        "google_maps": f"https://www.google.com/maps/place/{lat},{lon}",
        "geohack": f"https://geohack.toolforge.org/geohack.php?params={lat};{lon}"
    }

def lookup_barcode(barcode_data, barcode_type):
    """Looks up a barcode using Open Food Facts as a primary source."""
    if "EAN" in barcode_type or "UPC" in barcode_type:
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode_data}.json"
        try:
             response = requests.get(url)
             if response.status_code == 200:
                 data = response.json()
                 if data.get("status") == 1:
                     product = data.get("product", {})
                     return {
                         "product_name": product.get("product_name"),
                         "brand": product.get("brands"),
                         "url": f"https://world.openfoodfacts.org/product/{barcode_data}"
                     }
        except Exception:
             pass
    return {"status": "Lookup attempted, no specific product found or unsupported type."}

def execute_tool(tool_command):
    """Dispatcher for executing tools based on Gemini's request."""
    tool_name = tool_command.get("tool_name", "").lower()
    input_data = tool_command.get("input_data")
    
    if "whois" in tool_name:
        return run_whois(input_data)
    elif "reverse image" in tool_name or "lens" in tool_name:
         return run_reverse_image_search(input_data)
    elif "breach" in tool_name or "hibp" in tool_name:
         return check_email_breach(input_data)
    elif "map" in tool_name or "geo" in tool_name:
         # Expecting comma separated lat,lon
         try:
             lat, lon = map(float, input_data.split(","))
             return generate_map_links(lat, lon)
         except:
             return {"error": "Invalid coordinate format for map generation."}
    elif "barcode" in tool_name:
          return lookup_barcode(input_data, "EAN13") # Defaulting type for simple execution
    
    return {"status": "Tool not directly implemented by agent. Proceed manually.", "tool_requested": tool_name}
