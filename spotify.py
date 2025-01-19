import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
from decouple import config
import json

# Configure page settings
st.set_page_config(
    page_title="Spotify Track Fetcher",
    page_icon="🎵",
    layout="wide"
)

# Initialize Spotify client
def get_spotify_client():
    client_id = config('SPOTIFY_CLIENT_ID')
    client_secret = config('SPOTIFY_CLIENT_SECRET')
    
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id, 
        client_secret=client_secret
    )
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Extract Spotify ID from URL
def extract_spotify_id(url):
    patterns = {
        'track': r'track/([a-zA-Z0-9]{22})',
        'album': r'album/([a-zA-Z0-9]{22})',
        'playlist': r'playlist/([a-zA-Z0-9]{22})'
    }
    
    for content_type, pattern in patterns.items():
        match = re.search(pattern, url)
        if match:
            return content_type, match.group(1)
    return None, None

# Fetch track information
def get_track_info(sp, track_id):
    track = sp.track(track_id)
    return {
        'name': track['name'],
        'artist': track['artists'][0]['name'],
        'album': track['album']['name'],
        'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
        'duration_ms': track['duration_ms'],
        'preview_url': track['preview_url']
    }

# Fetch album information
def get_album_info(sp, album_id):
    album = sp.album(album_id)
    tracks = sp.album_tracks(album_id)['items']
    return {
        'name': album['name'],
        'artist': album['artists'][0]['name'],
        'image_url': album['images'][0]['url'] if album['images'] else None,
        'tracks': [{'name': track['name'], 'preview_url': track['preview_url']} for track in tracks]
    }

# Fetch playlist information
def get_playlist_info(sp, playlist_id):
    playlist = sp.playlist(playlist_id)
    tracks = playlist['tracks']['items']
    return {
        'name': playlist['name'],
        'owner': playlist['owner']['display_name'],
        'image_url': playlist['images'][0]['url'] if playlist['images'] else None,
        'tracks': [{
            'name': track['track']['name'],
            'artist': track['track']['artists'][0]['name'],
            'preview_url': track['track']['preview_url']
        } for track in tracks if track['track']]
    }

def main():
    st.title("🎵 Spotify Track Fetcher")
    st.write("Enter a Spotify URL (track, album, or playlist) to fetch its information")
    
    # URL input
    url = st.text_input("Enter Spotify URL:", placeholder="https://open.spotify.com/...")
    
    if url:
        try:
            sp = get_spotify_client()
            content_type, content_id = extract_spotify_id(url)
            
            if not content_type or not content_id:
                st.error("Invalid Spotify URL. Please enter a valid track, album, or playlist URL.")
                return
            
            with st.spinner("Fetching data..."):
                if content_type == 'track':
                    info = get_track_info(sp, content_id)
                    st.image(info['image_url'], width=300)
                    st.header(info['name'])
                    st.subheader(f"By {info['artist']}")
                    st.write(f"Album: {info['album']}")
                    if info['preview_url']:
                        st.audio(info['preview_url'])
                    
                elif content_type == 'album':
                    info = get_album_info(sp, content_id)
                    st.image(info['image_url'], width=300)
                    st.header(info['name'])
                    st.subheader(f"By {info['artist']}")
                    
                    for i, track in enumerate(info['tracks'], 1):
                        st.write(f"{i}. {track['name']}")
                        if track['preview_url']:
                            st.audio(track['preview_url'])
                
                elif content_type == 'playlist':
                    info = get_playlist_info(sp, content_id)
                    st.image(info['image_url'], width=300)
                    st.header(info['name'])
                    st.subheader(f"Created by {info['owner']}")
                    
                    for i, track in enumerate(info['tracks'], 1):
                        st.write(f"{i}. {track['name']} - {track['artist']}")
                        if track['preview_url']:
                            st.audio(track['preview_url'])
                            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
