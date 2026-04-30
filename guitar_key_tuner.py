"""
Guitar Tunerz Song Search Tool dk2033 jl4238
"""

import json
import math
import http.client
import requests
import base64
from datetime import datetime

# =============================================================================
# API LOGIN KEYS
# =============================================================================
SPOTIFY_CLIENT_ID     = "spotify_api_key"
SPOTIFY_CLIENT_SECRET = "spotify_api_secret"
RAPIDAPI_KEY          = "rapid_api_key"

# =============================================================================
# MUSIC MAPPING FOR TUNING LATER
# =============================================================================

STANDARD_TUNING = {
    "E2": 82.41,
    "A2": 110.00,
    "D3": 146.83,
    "G3": 196.00,
    "B3": 246.94,
    "E4": 329.63,
}

NOTE_TO_PITCH = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F":  5, "F#": 6, "Gb": 6, "G":  7, "G#": 8,
    "Ab": 8,"A":  9, "A#": 10,"Bb": 10,"B":  11,
}

# =============================================================================
# CLASS: SpotifyWebAPI
# =============================================================================

class SpotifyWebAPI:
    """
    Handles all communication with the Spotify Web API.
    - Authenticate user with API key login
    - Search the Spotify catalogue for songs
    - Return song data and Spotify song ID
    """

    AUTH_URL   = "https://accounts.spotify.com/api/token"
    SEARCH_URL = "https://api.spotify.com/v1/search"

    def __init__(self):
        self._token = None

    def authenticate(self):
        credentials = base64.b64encode(
            f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
        ).decode()
        try:
            r = requests.post(
                self.AUTH_URL,
                data={"grant_type": "client_credentials"},
                headers={"Authorization": f"Basic {credentials}"},
                timeout=10,
            )
            r.raise_for_status()
            self._token = r.json()["access_token"]
        except requests.exceptions.HTTPError:
            print("\n  [⚠] Spotify authentication failed. Check API Key.")
            raise SystemExit(1)
        except requests.exceptions.ConnectionError:
            print("\n  [⚠] No internet connection.")
            raise SystemExit(1)

    def search(self, query, limit=5):
        r = requests.get(
            self.SEARCH_URL,
            headers={"Authorization": f"Bearer {self._token}"},
            params={"q": query, "type": "track", "limit": limit},
            timeout=10,
        )
        r.raise_for_status()
        items = r.json().get("tracks", {}).get("items", [])
        return [
            {
                "name":   item["name"],
                "artist": item["artists"][0]["name"],
                "album":  item["album"]["name"],
                "id":     item["id"],
            }
            for item in items
        ]
# =============================================================================
# CLASS: SoundNetAPI
# =============================================================================

class SoundNetAPI:
    """
    Communicates with the SoundNet Track Analysis API via RapidAPI.
    Returns the song's key, mode, and tempo from the database.
    """

    HOST     = "track-analysis.p.rapidapi.com"
    ENDPOINT = "/pktx/spotify/{spotify_id}"

    def get_analysis(self, spotify_id):
        try:
            conn = http.client.HTTPSConnection(self.HOST)
            headers = {
                "x-rapidapi-key":  RAPIDAPI_KEY,
                "x-rapidapi-host": self.HOST,
                "Content-Type":    "application/json",
            }
            conn.request(
                "GET",
                self.ENDPOINT.format(spotify_id=spotify_id),
                headers=headers,
            )
            res  = conn.getresponse()
            data = res.read()

            if res.status == 404:
                return None

            parsed = json.loads(data.decode("utf-8"))
            return {
                "key":   parsed.get("key", ""),
                "mode":  parsed.get("mode", "major"),
                "tempo": parsed.get("tempo", 0),
            }
        except Exception:
            return None