﻿# Spotify Downloader

A Streamlit web application that allows users to fetch, download, and manage music from Spotify tracks, albums, and playlists.

## Features

- **Track Information**:
  - Display track details with album artwork
  - Show audio features (danceability, energy, valence, tempo)
  - Preview audio samples
  - Direct download functionality

- **Album Support**:
  - View complete album details
  - Display all tracks in album
  - Batch download entire albums
  - Album artwork for each track

- **Playlist Support**:
  - View playlist information
  - Show all tracks with their album artwork
  - Batch download entire playlists
  - Display playlist description and creator

- **Download Management**:
  - Downloads stored in local 'download' folder
  - Track download history
  - Built-in audio player for downloaded songs
  - Group downloaded songs by album
  - Automatic file organization

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
   - Create a `.env` file and add your credentials:
     ```
     SPOTIFY_CLIENT_ID=your_client_id_here
     SPOTIFY_CLIENT_SECRET=your_client_secret_here
     ```

## Usage

1. Run the application:
   ```bash
   streamlit run app.py
   ```

2. The app has two main tabs:
   - **Search & Download**: Search and download new tracks
   - **Downloaded Songs**: View and play your downloaded music

3. To download music:
   - Paste a Spotify URL (track/album/playlist)
   - Click the download button
   - Files are saved in the 'download' folder

4. To manage downloads:
   - Go to "Downloaded Songs" tab
   - Browse songs grouped by album
   - Use the built-in audio player
   - View download dates and details

## Supported URL Formats

- Tracks: `https://open.spotify.com/track/[id]`
- Albums: `https://open.spotify.com/album/[id]`
- Playlists: `https://open.spotify.com/playlist/[id]`

## File Structure

```
spotify/
├── app.py              # Main Streamlit application
├── spotify.py          # Spotify API integration
├── yt_download.py      # Download functionality
├── download/           # Downloaded music storage
│   └── downloads.json  # Download history database
├── .env               # API credentials
└── requirements.txt    # Project dependencies
```

## Notes

- Downloads are stored in the 'download' folder
- Download history is tracked in downloads.json
- The app automatically manages file organization
- Audio files are downloaded in MP3 format when available
