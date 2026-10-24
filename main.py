from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import re
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.terabox.com/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
}

def get_direct_link(terabox_url: str):
    try:
        # Terabox sometimes redirects to different domains
        session = requests.Session()
        response = session.get(terabox_url, headers=HEADERS, allow_redirects=True, timeout=10)
        html = response.text
        
        # Method 1: JSON State (Purana tarika)
        match = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});', html, re.DOTALL)
        if match:
            state_json = json.loads(match.group(1))
            file_info = state_json.get("file", {}).get("file_info", {})
            dlink = file_info.get("dlink")
            if dlink:
                return dlink

        # Method 2: Direct HTML Regex (Naya fallback)
        # Look for dlink in the HTML directly
        match = re.search(r'"dlink":"(https:\\/\\/[^"]+)"', html)
        if match:
            # Unescape the slashes
            return match.group(1).replace('\\/', '/')

        raise ValueError("Direct link nahi mila. Terabox ne structure change kar diya.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download")
def download_file(url: str = Query(...)):
    direct_link = get_direct_link(url)
    return RedirectResponse(url=direct_link)
