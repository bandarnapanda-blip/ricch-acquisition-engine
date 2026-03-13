import requests
import zipfile
import os
import io

url = "https://bin.ngrok.com/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
dest = "ngrok.zip"

print(f"Downloading ngrok from {url}...")
try:
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    
    with open(dest, "wb") as f:
        f.write(response.content)
    
    print("Download complete. Extracting...")
    with zipfile.ZipFile(dest, 'r') as zip_ref:
        zip_ref.extractall(".")
    
    print("Extraction complete. ngrok.exe should be in the current directory.")
except Exception as e:
    print(f"Failed to download/extract: {e}")
