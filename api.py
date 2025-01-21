from fastapi import FastAPI, HTTPException, Header
import requests
from spotify import get_track_info
from yt_download_api import get_download_url
import base64

app = FastAPI(title="Spotify Downloader API", version="1.0.0")

async def get_spotify_token(credentials: dict) -> str:
    """Get Spotify access token from credentials"""
    try:
        # Encode client credentials
        auth_header = base64.b64encode(
            f"{credentials['client_id']}:{credentials['client_secret']}".encode('utf-8')
        ).decode('utf-8')
        
        # Get token
        response = requests.post(
            'https://accounts.spotify.com/api/token',
            headers={
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={'grant_type': 'client_credentials'}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid Spotify credentials")
            
        return response.json()['access_token']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Spotify token: {str(e)}")

@app.get("/v1/track/{track_id}")
async def get_track_download_url(
    track_id: str,
    client_id: str = Header(...),
    client_secret: str = Header(...)
):
    """
    Get direct download URL for a Spotify track
    - Requires Spotify client_id and client_secret in headers
    - Returns track info and download URL
    """
    try:
        # Get access token
        access_token = await get_spotify_token({"client_id": client_id, "client_secret": client_secret})
        
        # Get track info
        track_info, error = get_track_info(access_token, track_id)
        if error:
            raise HTTPException(status_code=404, detail=error)
        
        # Get download URL
        download_url = get_download_url(track_info)
        if not download_url:
            raise HTTPException(status_code=404, detail="Could not find download URL")
        
        return {
            "status": "success",
            "track_info": track_info,
            "download_url": download_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 