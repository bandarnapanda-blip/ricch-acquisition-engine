import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Use a context that looks like a real user
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        await page.goto("https://search.yahoo.com/search?p=Epoxy+Garage+Flooring+in+Frisco,+Texas", timeout=20000)
        await page.wait_for_timeout(3000)
        
        content = await page.content()
        with open('debug.html', 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("HTML dumped to debug.html")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
