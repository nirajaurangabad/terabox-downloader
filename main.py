from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/download")
async def download_file(url: str = Query(...)):
    try:
        # Terabox ka internal API call
        share_url = url.split('s/')[-1].split('?')[0]
        api_url = f"https://www.terabox.com/share/list?shorturl={share_url}&root=1"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://www.terabox.com/"
        }

        async with httpx.AsyncClient() as client:
            res = await client.get(api_url, headers=headers)
            data = res.json()

            if data.get("errno") == 0 and data.get("list"):
                dlink = data["list"][0].get("dlink")
                if dlink:
                    return RedirectResponse(url=dlink)
            
            raise ValueError("Link nahi mila. Terabox API ne reject kiya.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
