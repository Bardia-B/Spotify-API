import yt_dlp
import random
import time
from pathlib import Path
import os

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
]

def get_random_headers():
    user_agent = random.choice(USER_AGENTS)
    return {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }

class QuietLogger:
    def debug(self, msg):
        if isinstance(msg, bytes):
            msg = msg.decode('utf-8', errors='ignore')
        if not msg.startswith('[debug]'):
            pass
    
    def warning(self, msg):
        pass
    
    def error(self, msg):
        if isinstance(msg, bytes):
            msg = msg.decode('utf-8', errors='ignore')
        print(f"Download Error: {msg}")

def get_download_url(track_info):
    """Get direct download URL for a track without downloading"""
    try:
        # Extract artist names if they're objects
        artists = [artist['name'] if isinstance(artist, dict) else artist for artist in track_info['artists']]
        track_name = track_info['name']
        search_query = f"{' '.join(artists)} {track_name} audio"
        
        ydl_opts = {
            'format': 'bestaudio',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'youtube_include_dash_manifest': False,
            'logger': QuietLogger()
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Search for the video
            search_results = ydl.extract_info(f"ytsearch1:{search_query}", download=False)
            
            if search_results and 'entries' in search_results and search_results['entries']:
                video_info = search_results['entries'][0]
                
                # Get the URL directly from the best format
                url = video_info.get('url')
                if url:
                    print(f"[debug] Invoking http downloader on \"{url}\"")
                    return url
                
                # If no direct URL, extract it from formats
                formats = video_info.get('formats', [])
                if formats:
                    # Filter audio-only formats
                    audio_formats = [f for f in formats if 
                                   f.get('acodec') != 'none' and 
                                   f.get('vcodec') in ['none', None]]
                    
                    if audio_formats:
                        # Get the best quality audio URL
                        best_audio = audio_formats[0]
                        url = best_audio.get('url')
                        if url:
                            print(f"[debug] Invoking http downloader on \"{url}\"")
                            return url
                    
        return None
    except Exception as e:
        print(f"Error getting download URL: {str(e)}")
        return None 