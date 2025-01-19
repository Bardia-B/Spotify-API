# Configure page settings first
import streamlit as st
st.set_page_config(
    page_title="Spotify Track Fetcher",
    page_icon="🎵",
    layout="wide"
)

# Then import other modules
from spotify import (
    get_access_token, extract_spotify_id, get_track_info,
    get_album_info, get_playlist_info, format_duration, format_date
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .track-container {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .artist-name {
        font-style: italic;
        color: #1DB954;
    }
    .download-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 8px 16px;
        background-color: #1DB954;
        color: white;
        border-radius: 20px;
        text-decoration: none;
        margin: 5px 0;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s;
        font-weight: bold;
    }
    .download-btn:hover {
        background-color: #1ed760;
    }
    .stButton>button {
        background-color: #1DB954;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 8px 16px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1ed760;
    }
    </style>
""", unsafe_allow_html=True)

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

def display_track(track, index=None):
    with st.container():
        st.markdown("---")
        cols = st.columns([1, 1, 3, 1, 1])
        
        # Track number
        with cols[0]:
            if index:
                st.write(f"**{index}.**")
        
        # Album cover
        with cols[1]:
            if track.get('album_image'):
                st.image(track['album_image'], width=60)
        
        # Track info
        with cols[2]:
            st.write(f"**{track['name']}**")
            st.markdown(f"*{', '.join(track['artists'])}*")
            if 'album' in track:
                st.write(f"💿 {track['album']}")
        
        # Duration
        with cols[3]:
            st.write(f"⏱️ {format_duration(track['duration_ms'])}")
        
        # Preview and download
        with cols[4]:
            if track.get('preview_url'):
                st.audio(track['preview_url'])
            st.button("⬇️ Download", key=f"download_{index}")

def main():
    st.title("🎵 Spotify Track Fetcher")
    st.write("Enter a Spotify URL (track, album, or playlist) to fetch its information")
    
    # Get access token
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
                    st.error(error)
                    return
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(info['image_url'], width=300)
                with col2:
                    st.header(info['name'])
                    st.markdown(f"*{', '.join(info['artists'])}*")
                    st.write(f"🎵 Album: {info['album']}")
                    st.write(f"📅 Released: {format_date(info['release_date'])}")
                    st.write(f"⏱️ Duration: {format_duration(info['duration_ms'])}")
                    st.write(f"🔗 [Open in Spotify]({info['external_urls']})")
                    st.button("⬇️ Download", key="download_single")
                
                if info['audio_features']:
                    st.subheader("Audio Features")
                    display_audio_features(info['audio_features'])
                
                if info['preview_url']:
                    st.subheader("Preview")
                    st.audio(info['preview_url'])
            
            elif content_type == 'album':
                info, error = get_album_info(access_token, content_id)
                if not info:
                    st.error(error)
                    return
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(info['image_url'], width=300)
                with col2:
                    st.header(info['name'])
                    st.markdown(f"*{', '.join(info['artists'])}*")
                    st.write(f"📅 Released: {format_date(info['release_date'])}")
                    st.write(f"🎵 Tracks: {info['total_tracks']}")
                
                st.subheader("Tracks")
                for track in info['tracks']:
                    display_track(track, track['track_number'])
            
            elif content_type == 'playlist':
                info, error = get_playlist_info(access_token, content_id)
                if not info:
                    st.error(error)
                    return
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(info['image_url'], width=300)
                with col2:
                    st.header(info['name'])
                    st.subheader(f"Created by {info['owner']}")
                    if info['description']:
                        st.write(info['description'])
                    st.write(f"🎵 Total tracks: {info['total_tracks']}")
                
                st.subheader("Tracks")
                for i, track in enumerate(info['tracks'], 1):
                    display_track(track, i)
                    if track['audio_features']:
                        display_audio_features(track['audio_features'])

if __name__ == "__main__":
    main()
