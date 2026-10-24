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
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")
            
            # Terabox page load hone ka wait
            await page.wait_for_timeout(3000)
            
            # Page se dlink nikalna
            dlink = await page.evaluate("() => window.__INITIAL_STATE__?.file?.file_info?.dlink")
            
            if not dlink:
                # agar state na mile toh HTML se dhundhna
                content = await page.content()
                import re
                match = re.search(r'"dlink":"(https:\\/\\/[^"]+)"', content)
                if match:
                    dlink = match.group(1).replace('\\/', '/')

            await browser.close()

            if dlink:
                return RedirectResponse(url=dlink)
            else:
                raise ValueError("Link nahi mila, terabox block kar raha hai.")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
