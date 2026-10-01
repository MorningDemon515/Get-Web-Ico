import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def get_website_favicon(site_url, save_dir="./favicons"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # 1. Initiate a network request
        response = requests.get(site_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        favicon_url = None
        
        # 2. Search for <link rel="icon"> or related tags
        # Matches common rel attribute values: icon, shortcut icon, apple-touch-icon, etc.
        icon_link = soup.find("link", rel=lambda x: x and ('icon' in x.lower() or 'shortcut' in x.lower()))
        
        if icon_link and icon_link.get("href"):
            # Automatically handle relative paths (such as /favicon.ico or ./assets/logo.png)
            favicon_url = urljoin(site_url, icon_link["href"])
        else:
            # 3. Backup solution: If it's not specified in the HTML, try the `/favicon.ico` file in the root directory.
            parsed_url = urlparse(site_url)
            favicon_url = f"{parsed_url.scheme}://{parsed_url.netloc}/favicon.ico"
            
        print(f"[+] Find the icon URL: {favicon_url}")
        
        # 4. Download and save the icon
        img_response = requests.get(favicon_url, headers=headers, timeout=10)
        if img_response.status_code == 200 and 'image' in img_response.headers.get('Content-Type', ''):
            os.makedirs(save_dir, exist_ok=True)
            domain = urlparse(site_url).netloc
            ext = favicon_url.split('.')[-1].split('?')[0]
            if len(ext) > 4 or not ext:
                ext = "ico"  # Default suffix
                
            file_path = os.path.join(save_dir, f"{domain}.{ext}")
            
            with open(file_path, "wb") as f:
                f.write(img_response.content)
            print(f"[✓] Successfully saved to: {file_path}")
            return file_path
        else:
            print("[-] Icon retrieval failed: Target URL is not a valid image or the request was blocked.")
            
    except Exception as e:
        print(f"[!] Crawling error ({site_url}): {e}")

# Example call
if __name__ == "__main__":
    get_website_favicon("https://www.github.com/")
