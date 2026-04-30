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