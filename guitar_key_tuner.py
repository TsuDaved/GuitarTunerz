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
        
# =============================================================================
# CLASS: MusicTheoryEngine
# =============================================================================

class MusicTheoryEngine:
    """
    Handles all music theory calculations needed to convert a detected
    key into per-string frequency targets for the motor controller.
    """

    STANDARD_KEY_INDEX = 4
    MAX_DROP           = 4
    KEY_DISPLAY = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]

    @staticmethod
    def parse_key_to_pitch(key_str):
        if not key_str:
            return MusicTheoryEngine.STANDARD_KEY_INDEX
        normalised = key_str.strip().capitalize()
        if len(normalised) > 1 and normalised[1] in ("#", "b"):
            normalised = normalised[0].upper() + normalised[1]
        return NOTE_TO_PITCH.get(normalised, MusicTheoryEngine.STANDARD_KEY_INDEX)

    @staticmethod
    def semitones_to_drop(target_pitch):
        diff = target_pitch - MusicTheoryEngine.STANDARD_KEY_INDEX
        if diff > 0:
            diff -= 12
        return max(diff, -MusicTheoryEngine.MAX_DROP)

    @staticmethod
    def target_freq(base_hz, semitones):
        return round(base_hz * (2 ** (semitones / 12)), 2)

    @staticmethod
    def to_cents(f1, f2):
        return round(1200 * math.log2(f2 / f1), 1)

    @staticmethod
    def build_key_string(raw_key, raw_mode):
        pitch    = MusicTheoryEngine.parse_key_to_pitch(raw_key)
        mode_str = "Major" if "major" in raw_mode.lower() else "Minor"
        return f"{MusicTheoryEngine.KEY_DISPLAY[pitch]} {mode_str}"

    @staticmethod
    def calculate_string_rows(semitones):
        rows = []
        for name, std in STANDARD_TUNING.items():
            tgt       = MusicTheoryEngine.target_freq(std, semitones)
            cents     = MusicTheoryEngine.to_cents(std, tgt)
            direction = ("loosen"    if semitones < 0 else
                         "tighten"   if semitones > 0 else
                         "no change")
            rows.append({
                "string":      name,
                "standard_hz": std,
                "target_hz":   tgt,
                "cents":       cents,
                "semitones":   semitones,
                "direction":   direction,
            })
        return rows
    
# =============================================================================
# CLASS: UserInterface
# =============================================================================

class UserInterface:
    """
    Handles all terminal input and output interactions with the user.
    """

    @staticmethod
    def print_banner():
        print("\n" + "=" * 54)
        print("   Guitar Tunerz Project - Song Key Detector")
        print("=" * 54)

    @staticmethod
    def get_song_input():
        while True:
            song = input("\n  Song name : ").strip()
            ok, err = UserInterface._validate(song)
            if ok:
                return song
            print(f"  [!] {err}")

    @staticmethod
    def get_artist_input():
        return input("  Artist    : (press Enter to skip) ").strip()

    @staticmethod
    def pick_track(candidates):
        print("\n  Spotify found these matches:\n")
        for i, t in enumerate(candidates, 1):
            print(f"    [{i}] \"{t['name']}\"  -  {t['artist']}  (Album: {t['album']})")
        print("    [0] None of these - search again\n")
        while True:
            raw = input(f"  Your choice [0-{len(candidates)}]: ").strip()
            if raw.isdigit() and 0 <= int(raw) <= len(candidates):
                n = int(raw)
                return candidates[n - 1] if n > 0 else None
            print(f"  [⚠] Please enter a number between 0 and {len(candidates)}.")

    @staticmethod
    def confirm_track(track):
        answer = input(
            f"\n  Use \"{track['name']}\" by {track['artist']}? [Y/n]: "
        ).strip().lower()
        return answer in ("", "y", "yes")

    @staticmethod
    def print_tuning_table(key_str, semitones, tempo, string_rows):
        print(f"\n  {'='*50}")
        print(f"  Key    : {key_str}")
        if tempo:
            print(f"  Tempo  : {tempo} BPM")
        print(f"  Drop   : {semitones} semitone(s) from E standard")
        print(f"  {'='*50}")
        print(f"\n  {'String':<6} {'Std Hz':>8}  {'Target Hz':>10}  {'Cents':>8}  Motor")
        print(f"  {'-'*50}")
        for s in string_rows:
            print(
                f"  {s['string']:<6} {s['standard_hz']:>8.2f}  "
                f"{s['target_hz']:>10.2f}  {s['cents']:>+8.1f}  "
                f"{s['direction'].upper()}"
            )

    @staticmethod
    def _validate(text):
        s = text.strip()
        if not s:
            return False, "Cannot be empty."
        if len(s) < 2:
            return False, "Too short (minimum 2 characters)."
        if not any(c.isalpha() for c in s):
            return False, "Must contain at least one letter."
        return True, ""