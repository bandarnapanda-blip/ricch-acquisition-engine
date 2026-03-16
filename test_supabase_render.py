import os
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def test_upload():
    url: str = SUPABASE_URL or ""
    key: str = SUPABASE_KEY or ""
    supabase: Client = create_client(url, key)

    test_html = "<!DOCTYPE html><html><body><h1>Supabase Client Test 7</h1></body></html>"
    filename = "rendering_test_client_7.html"
    bucket = "landing-pages"
    
    print(f"Uploading to {bucket}/{filename} via supabase client...")
    
    try:
        # Explicitly set Content-Type in file_options
        response = supabase.storage.from_(bucket).upload(
            path=filename,
            file=test_html.encode('utf-8'),
            file_options={
                "Content-Type": "text/html; charset=utf-8",
                "x-upsert": "true"
            }
        )
        print(f"Upload Success: {response}")
    except Exception as e:
        print(f"Upload Failed, trying update: {e}")
        try:
            response = supabase.storage.from_(bucket).update(
                path=filename,
                file=test_html.encode('utf-8'),
                file_options={"content-type": "text/html"}
            )
            print(f"Update Success: {response}")
        except Exception as e2:
            print(f"Update Failed: {e2}")
    
    # Create signed URL
    print("Generating signed URL...")
    try:
        # Create a signed URL for 1 hour
        signed_res = supabase.storage.from_(bucket).create_signed_url(filename, 3600)
        signed_url = signed_res.get('signedURL')
        print(f"Signed URL: {signed_url}")
        
        # Check signed URL headers
        head_signed = requests.head(signed_url)
        print(f"Signed Status: {head_signed.status_code}")
        print(f"Signed Content-Type: {head_signed.headers.get('Content-Type')}")
        print(f"Signed Full Headers: {dict(head_signed.headers)}")
    except Exception as e:
        print(f"Signed URL failed: {e}")

if __name__ == "__main__":
    test_upload()
