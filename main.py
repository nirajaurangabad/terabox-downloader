from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/download")
async def download_file(url: str = Query(...)):
    try:
        async with async_playwright() as p:
            # Memory bachane ke liye extra arguments
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
            )
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded")
            
            # Page load hone ka wait
            await page.wait_for_timeout(3000)
            
            dlink = await page.evaluate("() => window.__INITIAL_STATE__?.file?.file_info?.dlink")
            
            await browser.close()

            if dlink:
                return RedirectResponse(url=dlink)
            else:
                raise ValueError("Link nahi mila.")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
