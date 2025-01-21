import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from decouple import config
import base64
import urllib.parse
import pandas as pd

def get_auth_url():
    """Generate the authorization URL"""
    client_id = config('SPOTIFY_CLIENT_ID')
    redirect_uri = 'http://localhost:8501'
    scope = 'user-top-read'
    
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': scope
    }
    
    return f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"

def get_token_with_auth_code(code):
    """Get access token using authorization code"""
    try:
        client_id = config('SPOTIFY_CLIENT_ID')
        client_secret = config('SPOTIFY_CLIENT_SECRET')
        redirect_uri = 'http://localhost:8501'
        
        # Encode client credentials
        auth_header = base64.b64encode(
            f"{client_id}:{client_secret}".encode('utf-8')
        ).decode('utf-8')
        
        # Exchange code for token
        response = requests.post(
            'https://accounts.spotify.com/api/token',
            headers={
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri
            }
        )
        
        if response.status_code == 200:
            return response.json()['access_token'], None
        else:
            return None, f"Failed to get token: {response.status_code}"
            
    except Exception as e:
        return None, f"Error getting token: {str(e)}"

def get_user_top_items(access_token, item_type):
    """Get user's top tracks or artists"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"https://api.spotify.com/v1/me/top/{item_type}",
            headers=headers,
            params={'limit': 50, 'offset': 0}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error fetching top {item_type}: {str(e)}")
        return None

def get_new_releases(access_token, limit=50):
    """Get new releases"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            "https://api.spotify.com/v1/browse/new-releases",
            headers=headers,
            params={'limit': limit, 'offset': 0, 'country': 'US'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error fetching new releases: {str(e)}")
        return None

def get_featured_playlists(access_token, limit=50):
    """Get featured playlists"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            "https://api.spotify.com/v1/browse/featured-playlists",
            headers=headers,
            params={
                'limit': limit, 
                'offset': 0,
                'country': 'US',
                'locale': 'en_US'
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error fetching featured playlists: {str(e)}")
        return None

def create_releases_chart(new_releases):
    """Create a bar chart of new releases by popularity"""
    if not new_releases or 'albums' not in new_releases:
        return None
    
    albums_data = {
        'Album': [f"{album['name']} - {album['artists'][0]['name']}" 
                 for album in new_releases['albums']['items'][:10]],
        'Popularity': [album['popularity'] for album in new_releases['albums']['items'][:10]]
    }
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=albums_data['Album'],
        y=albums_data['Popularity'],
        marker_color='#1DB954'
    ))
    
    fig.update_layout(
        title='Top New Releases',
        xaxis_tickangle=-45,
        xaxis_title='Album',
        yaxis_title='Popularity Score',
        hovermode='x unified'
    )
    return fig

def create_genre_chart(new_releases):
    """Create a pie chart of genres from new releases"""
    if not new_releases or 'albums' not in new_releases:
        return None
    
    all_genres = []
    for album in new_releases['albums']['items']:
        if 'genres' in album:
            all_genres.extend(album['genres'])
    
    if not all_genres:
        return None
        
    genre_counts = Counter(all_genres)
    top_genres = dict(sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    fig = px.pie(
        values=list(top_genres.values()),
        names=list(top_genres.keys()),
        title='Popular Music Genres',
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False)
    return fig

def create_artist_chart(top_artists):
    """Create a bar chart of top artists by popularity"""
    if not top_artists or 'items' not in top_artists:
        return None
    
    artists_data = {
        'Artist': [artist['name'] for artist in top_artists['items'][:10]],
        'Popularity': [artist['popularity'] for artist in top_artists['items'][:10]]
    }
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=artists_data['Artist'],
        y=artists_data['Popularity'],
        marker_color='#1DB954'
    ))
    
    fig.update_layout(
        title='Top Artists',
        xaxis_tickangle=-45,
        xaxis_title='Artist',
        yaxis_title='Popularity Score',
        hovermode='x unified'
    )
    return fig

def create_tracks_chart(top_tracks):
    """Create a bar chart of top tracks by popularity"""
    if not top_tracks or 'items' not in top_tracks:
        return None
    
    tracks_data = {
        'Track': [track['name'] for track in top_tracks['items'][:10]],
        'Popularity': [track['popularity'] for track in top_tracks['items'][:10]]
    }
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=tracks_data['Track'],
        y=tracks_data['Popularity'],
        marker_color='#1DB954'
    ))
    
    fig.update_layout(
        title='Top Tracks',
        xaxis_tickangle=-45,
        xaxis_title='Track',
        yaxis_title='Popularity Score',
        hovermode='x unified'
    )
    return fig

def display_user_stats():
    """Display user's Spotify statistics"""
    st.title("📊 My Spotify Stats")
    
    # Check if we have a code in URL parameters
    if 'code' in st.query_params:
        code = st.query_params['code']
        access_token, error = get_token_with_auth_code(code)
        if access_token:
            st.session_state['access_token'] = access_token
            # Clear URL parameters
            st.query_params.clear()
    
    # Check if we have a token in session state
    if 'access_token' not in st.session_state:
        # Show login button
        auth_url = get_auth_url()
        st.write("Please login to Spotify to view your statistics:")
        st.markdown(f"[Login to Spotify]({auth_url})")
        return
    
    # Use the token to fetch data
    access_token = st.session_state['access_token']
    
    # Fetch user's top items
    with st.spinner("Loading your stats..."):
        top_artists = get_user_top_items(access_token, 'artists')
        top_tracks = get_user_top_items(access_token, 'tracks')
        
        if top_artists and top_tracks:
            # Create two columns for top level stats
            col1, col2 = st.columns(2)
            
            with col1:
                # Top Artists Section - ordered by most listened
                st.subheader("🎤 Your Top 20 Artists")
                artists_data = pd.DataFrame({
                    'Artist': [artist['name'] for artist in top_artists['items'][:20]],
                    'Listens': range(20, 0, -1)  # 20 to 1 for visualization
                })
                
                st.bar_chart(
                    artists_data,
                    x='Artist',
                    y='Listens',
                    use_container_width=True
                )
            
            with col2:
                # Genre Pie Chart
                st.subheader("🎵 Your Top Genres")
                all_genres = []
                for artist in top_artists['items']:
                    all_genres.extend(artist['genres'])
                
                genre_counts = Counter(all_genres)
                top_genres = dict(sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:5])
                
                fig = px.pie(
                    values=list(top_genres.values()),
                    names=list(top_genres.keys()),
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(showlegend=True, height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Top Tracks Section - ordered by most listened
            st.subheader("🎼 Your Top 20 Tracks")
            
            # Create two columns for tracks visualization
            track_col1, track_col2 = st.columns(2)
            
            with track_col1:
                # Display tracks in a clean table
                display_df = pd.DataFrame({
                    'Rank': range(1, 21),
                    'Track': [f"{track['name']}" for track in top_tracks['items'][:20]],
                    'Artist': [track['artists'][0]['name'] for track in top_tracks['items'][:20]]
                })
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
            
            with track_col2:
                # Create a bar chart for top tracks
                tracks_data = pd.DataFrame({
                    'Track': [f"{track['name']}" for track in top_tracks['items'][:20]],
                    'Listens': range(20, 0, -1)  # 20 to 1 for visualization
                })
                
                st.bar_chart(
                    tracks_data,
                    x='Track',
                    y='Listens',
                    use_container_width=True
                )

if __name__ == "__main__":
    display_user_stats() 