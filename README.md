# Spotify Track Fetcher

A Streamlit web application that allows users to fetch and display information about Spotify tracks, albums, and playlists.

## Features

- Fetch track information including preview audio
- Display album details and tracks
- Show playlist contents with track previews
- Clean and modern UI using Streamlit

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up Spotify API credentials:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new application
   - Copy the Client ID and Client Secret
   - Rename `.env.example` to `.env` and fill in your credentials:
     ```
     SPOTIFY_CLIENT_ID=your_client_id_here
     SPOTIFY_CLIENT_SECRET=your_client_secret_here
     ```

## Usage

1. Run the application:
   ```bash
   streamlit run spotify.py
   ```

2. Open your browser and go to the URL shown in the terminal (usually http://localhost:8501)

3. Enter a Spotify URL for a track, album, or playlist

4. The application will display the relevant information and audio previews when available

## Supported URL Formats

- Tracks: `https://open.spotify.com/track/[id]`
- Albums: `https://open.spotify.com/album/[id]`
- Playlists: `https://open.spotify.com/playlist/[id]`
