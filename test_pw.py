from playwright.sync_api import sync_playwright

def test():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            print("Playwright launched successfully!")
            browser.close()
    except Exception as e:
        print(f"Playwright error: {e}")

if __name__ == "__main__":
    test()
