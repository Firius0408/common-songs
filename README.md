# Common Songs App

Simple python script to update playlists containing common songs between users

## Setup

This project uses Python >=3.6 and pipenv

Spotify API keys, playlist ID, and refresh token should be placed in `.env`:

`SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, and `SPOTIFY_REFRESH_TOKEN`

The playlists to be tracked should be placed `data.json` under `commonsongs` in this format:

List[Tuple[Users: List[str], PlaylistID: str]]

```python
python3 -m pip install pipenv
pipenv install
```

## Updating Playlists

The `common_songs.py` script scans for songs added to a user and adds it to the playlist

`pipenv run python3 common_songs.py`

Copyright © Brian Cheng 2021
