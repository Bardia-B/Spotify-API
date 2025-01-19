import requests
import json
from decouple import config
import re
from datetime import datetime
from spotipy.exceptions import SpotifyException
import streamlit as st

BASE_URL = "https://api.spotify.com/v1"

def get_access_token():
    try:
        client_id = config('SPOTIFY_CLIENT_ID')
        client_secret = config('SPOTIFY_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            return None, "Spotify credentials not found. Please check your .env file."
        
        # Get access token using client credentials flow
        auth_response = requests.post(
            'https://accounts.spotify.com/api/token',
            data={
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret,
            }
        )
        
        if auth_response.status_code != 200:
            return None, "Failed to get access token"
            
        auth_data = auth_response.json()
        return auth_data['access_token'], None
    except Exception as e:
        return None, f"Failed to get access token: {str(e)}"

def get_headers(access_token):
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

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

def get_audio_features(access_token, track_ids):
    if not isinstance(track_ids, list):
        track_ids = [track_ids]
    
    try:
        features = []
        for i in range(0, len(track_ids), 50):
            batch = track_ids[i:i + 50]
            response = requests.get(
                f"{BASE_URL}/audio-features",
                headers=get_headers(access_token),
                params={'ids': ','.join(batch)}
            )
            if response.status_code == 200:
                batch_features = response.json()['audio_features']
                if batch_features:
                    features.extend(batch_features)
        return {track_ids[i]: feat for i, feat in enumerate(features) if feat} if features else {}
    except Exception as e:
        print(f"Could not fetch audio features: {str(e)}")
        return {}

def get_track_info(access_token, track_id):
    try:
        response = requests.get(
            f"{BASE_URL}/tracks/{track_id}",
            headers=get_headers(access_token)
        )
        
        if response.status_code != 200:
            return None, f"Failed to fetch track data (Status: {response.status_code})"
            
        track_data = response.json()
        audio_features = get_audio_features(access_token, track_id)
        
        return {
            'name': track_data['name'],
            'artists': [artist['name'] for artist in track_data['artists']],
            'album': track_data['album']['name'],
            'album_type': track_data['album']['album_type'],
            'release_date': track_data['album']['release_date'],
            'image_url': track_data['album']['images'][0]['url'] if track_data['album']['images'] else None,
            'duration_ms': track_data['duration_ms'],
            'preview_url': track_data['preview_url'],
            'popularity': track_data['popularity'],
            'external_urls': track_data['external_urls']['spotify'],
            'audio_features': audio_features.get(track_id)
        }, None
    except Exception as e:
        return None, f"Error fetching track information: {str(e)}"

def get_album_info(access_token, album_id):
    try:
        album_response = requests.get(
            f"{BASE_URL}/albums/{album_id}",
            headers=get_headers(access_token)
        )
        
        if album_response.status_code != 200:
            return None, f"Failed to fetch album data (Status: {album_response.status_code})"
            
        album_data = album_response.json()
        
        return {
            'name': album_data['name'],
            'artists': [artist['name'] for artist in album_data['artists']],
            'release_date': album_data['release_date'],
            'total_tracks': album_data['total_tracks'],
            'image_url': album_data['images'][0]['url'] if album_data['images'] else None,
            'external_urls': album_data['external_urls']['spotify'],
            'tracks': [{
                'name': track['name'],
                'artists': [artist['name'] for artist in track['artists']],
                'duration_ms': track['duration_ms'],
                'preview_url': track['preview_url'],
                'track_number': track['track_number'],
                'album_image': album_data['images'][0]['url'] if album_data['images'] else None
            } for track in album_data['tracks']['items']]
        }, None
    except Exception as e:
        return None, f"Error fetching album information: {str(e)}"

def get_playlist_info(access_token, playlist_id):
    try:
        playlist_response = requests.get(
            f"{BASE_URL}/playlists/{playlist_id}",
            headers=get_headers(access_token),
            params={
                'fields': 'id,name,description,images,owner.display_name,followers.total,public,tracks.items(track(id,name,duration_ms,album(name,images),artists(name,id),preview_url))'
            }
        )
        
        if playlist_response.status_code != 200:
            return None, f"Failed to fetch playlist data (Status: {playlist_response.status_code})"
            
        playlist_data = playlist_response.json()
        tracks = []
        track_ids = []
        
        for item in playlist_data['tracks']['items']:
            if item['track']:
                track = item['track']
                track_ids.append(track['id'])
                tracks.append({
                    'id': track['id'],
                    'name': track['name'],
                    'artists': [artist['name'] for artist in track['artists']],
                    'album': track['album']['name'],
                    'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'duration_ms': track['duration_ms'],
                    'preview_url': track.get('preview_url')
                })
        
        audio_features = get_audio_features(access_token, track_ids)
        
        for track in tracks:
            track['audio_features'] = audio_features.get(track['id'])
        
        return {
            'name': playlist_data['name'],
            'owner': playlist_data['owner']['display_name'],
            'description': playlist_data.get('description'),
            'image_url': playlist_data['images'][0]['url'] if playlist_data['images'] else None,
            'total_tracks': len(tracks),
            'tracks': tracks
        }, None
    except Exception as e:
        return None, f"Error fetching playlist information: {str(e)}"

def format_duration(ms):
    seconds = int((ms / 1000) % 60)
    minutes = int((ms / (1000 * 60)) % 60)
    return f"{minutes}:{seconds:02d}"

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%B %d, %Y")
    except:
        return date_str

def display_audio_features(features):
    if not features:
        return
    
    try:
        cols = st.columns(4)
        with cols[0]:
            st.metric("Danceability", f"{int(features['danceability'] * 100)}%")
        with cols[1]:
            st.metric("Energy", f"{int(features['energy'] * 100)}%")
        with cols[2]:
            st.metric("Valence", f"{int(features['valence'] * 100)}%")
        with cols[3]:
            st.metric("Tempo", f"{int(features['tempo'])} BPM")
    except Exception as e:
        st.warning("Could not display audio features")

def main():
    st.title("🎵 Spotify Track Fetcher")
    st.write("Enter a Spotify URL (track, album, or playlist) to fetch its information")
    
    # Check for credentials first
    access_token, error = get_access_token()
    if not access_token:
        st.error(error)
        st.info("""
        1. Create a Spotify Developer account at https://developer.spotify.com
        2. Create a new application
        3. Copy your Client ID and Client Secret
        4. Add them to your .env file:
           ```
           SPOTIFY_CLIENT_ID=your_client_id_here
           SPOTIFY_CLIENT_SECRET=your_client_secret_here
           ```
        """)
        return
    
    # URL input
    url = st.text_input("Enter Spotify URL:", placeholder="https://open.spotify.com/...")
    
    if url:
        content_type, content_id = extract_spotify_id(url)
        
        if not content_type or not content_id:
            st.error("Invalid Spotify URL. Please enter a valid track, album, or playlist URL.")
            return
        
        with st.spinner("Fetching data..."):
            if content_type == 'track':
                info, error = get_track_info(access_token, content_id)
                if not info:
                    return
                
                # Display track information
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(info['image_url'], width=300)
                with col2:
                    st.header(info['name'])
                    st.subheader("By " + ", ".join(info['artists']))
                    st.write(f"🎵 Album: {info['album']}")
                    st.write(f"📅 Released: {format_date(info['release_date'])}")
                    st.write(f"⏱️ Duration: {format_duration(info['duration_ms'])}")
                    st.write(f"🎯 Popularity: {info['popularity']}/100")
                    if info['explicit']:
                        st.write("🔞 Explicit")
                    st.write(f"🔗 [Open in Spotify]({info['external_urls']})")
                
                if info['audio_features']:
                    st.subheader("Audio Features")
                    display_audio_features(info['audio_features'])
                
                if info['preview_url']:
                    st.subheader("Preview")
                    st.audio(info['preview_url'])
                
            elif content_type == 'album':
                info, error = get_album_info(access_token, content_id)
                if not info:
                    return
                
                # Display album information
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(info['image_url'], width=300)
                with col2:
                    st.header(info['name'])
                    st.subheader("By " + ", ".join(info['artists']))
                    st.write(f"📅 Released: {format_date(info['release_date'])}")
                    st.write(f"💿 Label: {info['label']}")
                    st.write(f"🎵 Tracks: {info['total_tracks']}")
                    st.write(f"🎯 Popularity: {info['popularity']}/100")
                    st.write(f"🔗 [Open in Spotify]({info['external_urls']})")
                
                # Display tracks
                st.subheader("Tracks")
                for track in info['tracks']:
                    with st.container():
                        st.markdown("---")
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.image(track['album_image'], width=100)
                            st.write(f"**{track['track_number']}. {track['name']}**")
                            st.write("By " + ", ".join(track['artists']))
                            if track['explicit']:
                                st.write("🔞 Explicit")
                        with col2:
                            st.write(f"⏱️ {format_duration(track['duration_ms'])}")
                            if track['preview_url']:
                                st.audio(track['preview_url'])
            
            elif content_type == 'playlist':
                info, error = get_playlist_info(access_token, content_id)
                if not info:
                    return
                
                # Display playlist information
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(info['image_url'], width=300)
                with col2:
                    st.header(info['name'])
                    st.subheader(f"Created by {info['owner']}")
                    if info['description']:
                        st.write(info['description'])
                    st.write(f"👥 Followers: {info['followers']:,}")
                    st.write(f"🎵 Total tracks: {info['total_tracks']}")
                    st.write("🔒 " + ("Public" if info['public'] else "Private") + " playlist")
                
                # Display tracks
                st.subheader("Tracks")
                for i, track in enumerate(info['tracks'], 1):
                    with st.container():
                        st.markdown("---")
                        col1, col2, col3 = st.columns([1, 2, 1])
                        
                        with col1:
                            if track['album_image']:
                                st.image(track['album_image'], width=100)
                        
                        with col2:
                            st.write(f"**{i}. {track['name']}**")
                            st.write("By " + ", ".join(track['artists']))
                            st.write(f"💿 Album: {track['album']}")
                            if track['explicit']:
                                st.write("🔞 Explicit")
                            st.write(f"📅 Added: {track['added_at'][:10]}")
                        
                        with col3:
                            st.write(f"⏱️ {format_duration(track['duration_ms'])}")
                            if track['preview_url']:
                                st.audio(track['preview_url'])
                        
                        if track['audio_features']:
                            display_audio_features(track['audio_features'])

if __name__ == "__main__":
    main()
