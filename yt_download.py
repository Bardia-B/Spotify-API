import yt_dlp
import os
import random
import time
from pathlib import Path
import streamlit as st
import json

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
        st.error(f"Download Error: {msg}")

def create_download_dir():
    """Create a downloads directory in the current folder"""
    download_dir = os.path.join(os.getcwd(), "download")
    os.makedirs(download_dir, exist_ok=True)
    return download_dir

def download_with_retry(track_info, download_dir, max_retries=3):
    artists = track_info['artists']
    track_name = track_info['name']
    search_query = f"{' '.join(artists)} {track_name} audio"
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                time.sleep(random.uniform(2, 5))

            headers = get_random_headers()
            
            # Create a filename based on track info
            safe_filename = f"{track_name} - {', '.join(artists)}".replace('/', '_').replace('\\', '_')
            output_template = os.path.join(download_dir, f"{safe_filename}.%(ext)s")

            ydl_opts = {
                'format': 'bestaudio[ext=mp3]/bestaudio[ext=m4a]/bestaudio',  # Prefer MP3 format directly
                'outtmpl': output_template,
                'noplaylist': True,
                'logger': QuietLogger(),
                'no_warnings': True,
                'quiet': True,
                'nocheckcertificate': True,
                'http_headers': headers,
                'socket_timeout': 30,
                'retries': 3,
                'ignoreerrors': True,
                'no_color': True,
                'extract_audio': True,
                'prefer_ffmpeg': False  # Don't use ffmpeg
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    search_url = f"ytsearch1:{search_query}"
                    info = ydl.extract_info(search_url, download=True)
                    
                    if info and 'entries' in info and info['entries']:
                        # Find the downloaded file
                        files = list(Path(download_dir).glob(f"{safe_filename}.*"))
                        if files:
                            # If the file isn't MP3, try to rename it
                            if files[0].suffix.lower() != '.mp3':
                                new_path = files[0].with_suffix('.mp3')
                                os.rename(files[0], new_path)
                                return str(new_path)
                            return str(files[0])
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise Exception(f"Failed to download: {str(e)}")
                    continue

            time.sleep(random.uniform(1, 3))

        except Exception as e:
            if attempt == max_retries - 1:
                raise Exception(f"All download attempts failed: {str(e)}")

    raise Exception("Download failed after all attempts")

def get_downloads_db_path():
    """Get the path to the downloads database file"""
    return os.path.join(os.getcwd(), "download", "downloads.json")

def load_downloads_db():
    """Load the downloads database"""
    db_path = get_downloads_db_path()
    if os.path.exists(db_path):
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'tracks': []}
    return {'tracks': []}

def save_downloads_db(db):
    """Save the downloads database"""
    db_path = get_downloads_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def add_to_downloads(track_info, file_path):
    """Add a track to the downloads database"""
    db = load_downloads_db()
    track_entry = {
        'name': track_info['name'],
        'artists': track_info['artists'],
        'file_path': file_path,
        'downloaded_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'album': track_info.get('album', ''),
        'album_image': track_info.get('album_image', track_info.get('image_url', ''))
    }
    
    # Check if track already exists
    existing = next((t for t in db['tracks'] if t['file_path'] == file_path), None)
    if not existing:
        db['tracks'].append(track_entry)
        save_downloads_db(db)

def get_downloaded_tracks():
    """Get list of downloaded tracks"""
    db = load_downloads_db()
    # Filter out tracks whose files no longer exist
    existing_tracks = [
        track for track in db['tracks']
        if os.path.exists(track['file_path'])
    ]
    # Update the database if some files were removed
    if len(existing_tracks) != len(db['tracks']):
        db['tracks'] = existing_tracks
        save_downloads_db(db)
    return existing_tracks

def download_track(track_info):
    """Download a single track"""
    try:
        download_dir = create_download_dir()
        file_path = download_with_retry(track_info, download_dir)
        if file_path:
            add_to_downloads(track_info, file_path)
        return file_path
    except Exception as e:
        st.error(f"Failed to download track: {str(e)}")
        return None

def download_tracks(tracks_info):
    """Download multiple tracks"""
    download_dir = create_download_dir()
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, track in enumerate(tracks_info):
        try:
            status_text.text(f"Downloading {i+1}/{len(tracks_info)}: {track['name']}")
            file_path = download_with_retry(track, download_dir)
            if file_path:
                add_to_downloads(track, file_path)
            results.append((True, file_path))
        except Exception as e:
            results.append((False, str(e)))
        
        progress_bar.progress((i + 1) / len(tracks_info))
    
    status_text.text("Download completed!")
    return results
