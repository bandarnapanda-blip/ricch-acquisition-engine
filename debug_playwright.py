from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Navigating to DuckDuckGo...")
        page.goto("https://duckduckgo.com/?q=Solar+Hills+Beverly+Hills")
        time.sleep(5)
        page.screenshot(path="playwright_debug.png")
        print(f"Page Title: {page.title()}")
        browser.close()

if __name__ == "__main__":
    run()
