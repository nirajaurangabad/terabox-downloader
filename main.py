from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import re

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/download")
async def download_file(url: str = Query(...)):
    try:
        # Link ko clean karna
        url = url.strip()
        
        # Browser jaisa fake headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.terabox.com/",
            "Connection": "keep-alive"
        }

        async with httpx.AsyncClient(follow_redirects=True) as client:
            # 1. Page fetch karo
            response = await client.get(url, headers=headers)
            html = response.text

            # 2. HTML me se 'dlink' ya 'downloadLink' nikalne ki koshish
            # Regex patterns alag-alag domains ke liye
            patterns = [
                r'"dlink":"(https:\\/\\/[^"]+)"',
                r'"downloadLink":"(https:\\/\\/[^"]+)"',
                r'"url":"(https:\\/\\/.*?\.terabox\.com\\/[^"]+)"'
            ]

            for pattern in patterns:
                match = re.search(pattern, html)
                if match:
                    # Slash escape hatana (\/ -> /)
                    direct_link = match.group(1).replace('\\/', '/')
                    return RedirectResponse(url=direct_link)

            raise ValueError("Direct link nahi mila. Terabox ne structure badla hai ya verify manga hai.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
