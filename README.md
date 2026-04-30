# GuitarTunerz

Repository for Project Week 3 - Guitar Tuning Device.

## Project Overview

This repository contains the Python code for the Guitar Tunerz song search tool.
The tool uses the Spotify API and SoundNet API to detect the musical key of a song
and calculate the per-string detuning instructions for an autonomous guitar tuning device.

## Branch: Song Search Pipeline

This branch documents the development of the full song search and tuning pipeline.

### Purpose of the Change

The purpose of this branch was to build the complete software pipeline including:
- Spotify API integration for song searching
- SoundNet API integration for key and tempo retrieval
- Music theory calculations for per-string detuning
- Terminal user interface for song selection
- File output for motor controller instructions

### Files Affected
- `guitar_key_tuner.py`
- `README.md`

### Summary of Changes
- Added API credentials and standard tuning constants
- Added SpotifyWebAPI class for authentication and song search
- Added SoundNetAPI class for musical key and tempo retrieval
- Added MusicTheoryEngine class for frequency and semitone calculations
- Added UserInterface class for terminal input and output
- Added OutputWriter class for txt and json file writing
- Added GuitarTuner main pipeline class to coordinate all components

### Why Version Control Was Used

Each class was developed and committed independently so that changes could be
isolated, reviewed, and tested before being integrated into the main branch.

## Setup

```bash
pip install requests
python guitar_key_tuner.py
```