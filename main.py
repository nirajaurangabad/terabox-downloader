from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import re
import json

app = FastAPI()

# CORS lagana zaroori hai taaki tera HTML isse baat kar sake
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Referer": "https://www.terabox.com/",
}

def get_direct_link(terabox_url: str):
    try:
        response = requests.get(terabox_url, headers=HEADERS, allow_redirects=True)
        response.raise_for_status()
        html = response.text
        match = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});', html, re.DOTALL)
        
        if not match:
            raise ValueError("State not found")
            
        state_json = json.loads(match.group(1))
        file_info = state_json.get("file", {}).get("file_info", {})
        dlink = file_info.get("dlink")
        
        if not dlink:
            raise ValueError("Direct link not found")
            
        return dlink
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download")
def download_file(url: str = Query(...)):
    direct_link = get_direct_link(url)
    return RedirectResponse(url=direct_link)