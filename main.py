from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright
import os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# TERA LOGS ME YE PATH DIKHA HAI, ISKO DIRECT DAAL RAHE HAIN
CHROME_PATH = "/opt/render/.cache/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell"

@app.get("/download")
async def download_file(url: str = Query(...)):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                executable_path=CHROME_PATH,  # FORCE PATH
                args=[
                    "--no-sandbox", 
                    "--disable-dev-shm-usage", 
                    "--disable-gpu",
                    "--single-process"
                ]
            )
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded")
            
            await page.wait_for_timeout(4000)
            
            dlink = await page.evaluate("() => window.__INITIAL_STATE__?.file?.file_info?.dlink")
            
            if not dlink:
                content = await page.content()
                import re
                match = re.search(r'"dlink":"(https:\\/\\/[^"]+)"', content)
                if match:
                    dlink = match.group(1).replace('\\/', '/')

            await browser.close()

            if dlink:
                return RedirectResponse(url=dlink)
            else:
                raise ValueError("Link nahi mila. Terabox ne block kiya ya file delete ho gayi.")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
