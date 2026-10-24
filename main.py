from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/download")
async def download_file(url: str = Query(...)):
    try:
        # 1. Terabox ka shorturl nikalna
        shorturl = url.split('s/')[-1].split('?')[0]
        
        # 2. Terabox ka internal API URL
        api_url = "https://www.terabox.com/share/list"
        
        # 3. Proper Headers (bina iske block karega)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": f"https://www.terabox.com/s/{shorturl}",
            "Accept": "application/json, text/plain, */*"
        }
        
        params = {
            "shorturl": shorturl,
            "root": "1"
        }

        async with httpx.AsyncClient() as client:
            res = await client.get(api_url, headers=headers, params=params)
            data = res.json()

            # 4. Link nikalna (terabox ke response se)
            if data.get("errno") == 0 and data.get("list"):
                dlink = data["list"][0].get("dlink")
                if dlink:
                    return RedirectResponse(url=dlink)
            
            raise ValueError(f"Reject: {data}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
