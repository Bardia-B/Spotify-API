# Spotify Downloader

A dual-interface application for downloading Spotify music. The project consists of two independent parts:
1. A standalone Streamlit web application for interactive use
2. A separate FastAPI backend for developers who want to integrate the download functionality into their own applications

## Features

### Streamlit Web Interface (Standalone App)
- Search and download Spotify tracks, albums, and playlists
- View track details, album artwork, and audio features
- Built-in audio player for previews
- Download history tracking
- Batch download support for albums and playlists
- Works independently without needing the API backend
- View your personal Spotify statistics:
  - Top tracks and listening history
  - Most played artists
  - Favorite genres visualization
  - Music taste analysis with interactive charts
  - Listening trends and patterns

### FastAPI Backend (Optional API)
- RESTful API for developers
- Direct download URLs for integration into other applications
- Simple authentication via headers
- Clean JSON responses
- Versioned endpoints (v1)

## Setup

1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd spotify-downloader
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Spotify API Configuration**
   1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   2. Create a new application
   3. Note your Client ID and Client Secret
   4. Add redirect URI in your Spotify Developer Dashboard:
      - For Streamlit: Your local Streamlit URL (typically `http://localhost:8501`, but may vary)
      - For API: Your API server URL (if using the API)
   5. Create `.env` file:
      ```env
      SPOTIFY_CLIENT_ID=your_client_id_here
      SPOTIFY_CLIENT_SECRET=your_client_secret_here
      ```

## Usage

### Streamlit Interface (Main Application)

1. **Start the App**
   ```bash
   streamlit run app.py
   # If the above doesn't work, try:
   python -m streamlit run app.py
   ```
   The app will open in your default browser at your local Streamlit URL.

2. **Features**
   - Search: Enter Spotify URLs (track/album/playlist)
   - Download: Click download button
   - History: View downloaded tracks
   - Player: Built-in audio player for previews

### FastAPI Backend (Optional API for Developers)

1. **Start the API Server**
   ```bash
   uvicorn api:app --reload
   # If the above doesn't work, try:
   python -m uvicorn api:app --reload
   ```
   The API will start on your local server.

2. **API Endpoints**

   - Get Track Download URL:
     ```
     GET /v1/track/{track_id}
     Headers:
       client-id: your_spotify_client_id
       client-secret: your_spotify_client_secret
     ```
     Response:
     ```json
     {
       "status": "success",
       "track_info": {
         "name": "Track Name",
         "artists": ["Artist Name"],
         "album": "Album Name",
         ...
       },
       "download_url": "https://..."
     }
     ```

3. **API Authentication**
   - Required Headers:
     - `client-id`: Your Spotify Client ID
     - `client-secret`: Your Spotify Client Secret
   - These credentials are used to authenticate with Spotify's API

## How It Works

### Download Process
1. User provides Spotify URL/ID
2. Application fetches track metadata from Spotify API
3. The track information is passed to yt-dlp library
4. yt-dlp searches for the best matching audio
5. For Streamlit app: yt-dlp downloads the file locally
6. For API: yt-dlp returns the direct download URL

### Streamlit App Flow
1. User enters Spotify URL
2. App fetches track metadata from Spotify
3. Uses yt-dlp to search and download audio
4. Saves to local 'download' directory
5. Updates download history

### API Flow (For Developers)
1. Receive request with track ID and credentials
2. Authenticate with Spotify using provided credentials
3. Fetch track metadata from Spotify
4. Use yt-dlp to search and get download URL
5. Return URL in response

## Supported URLs
- Track: `https://open.spotify.com/track/[id]`
- Album: `https://open.spotify.com/album/[id]`
- Playlist: `https://open.spotify.com/playlist/[id]`

## Notes
- The Streamlit app and API are completely independent
- Downloads are stored in the 'download' directory (Streamlit only)
- API returns temporary download URLs (for developers)
- Both interfaces require Spotify API credentials
- Download history is maintained for Streamlit interface only
- Uses yt-dlp library for searching and downloading audio
- Spotify stats feature is only available in the Streamlit interface
- Stats include personalized music analysis and visualizations
- User authentication required for viewing personal stats



