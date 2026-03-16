from playwright.sync_api import sync_playwright
import find_leads

def test():
    print(f"DEBUG: sync_playwright type: {type(sync_playwright)}")
    try:
        with sync_playwright() as p:
            print("Successfully launched Playwright from test script!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
