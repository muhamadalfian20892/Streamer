# Streamer App

Streamer App is an accessible audio and media player built with wxPython and libmpv for Windows. It is designed specifically for screen reader users (including NVDA) and live content streamers.

## Key Features

- **Accessibility First**: Every single control, slider, button, and menu item is labeled and screen reader friendly (`SetName` and `SetToolTip`). Includes automatic NVDA speech announcements and boundary audio cues.
- **Bilingual Interface**: Switch between Indonesian (Bahasa Indonesia) and English on the fly without needing to restart the application.
- **Persistent Audio & Settings**: Automatically remembers volume level, selected audio output device, equalizer preset, last played track position, and window geometry across application restarts.
- **Audio Processing**:
  - Equalizer presets: Flat, Bass Boost, Treble Boost, Vocal Boost.
  - Dynamic audio normalization to keep volume levels balanced across different media tracks.
  - Stereo downmix to Mono for single-ear monitoring or streaming.
  - Smooth audio fading on play, pause, seek, and track transitions.
- **Interface Modes**:
  - **Standard Mode**: Clean, streamlined interface focusing on essential playback controls.
  - **Advanced Mode**: Expands additional stream-oriented controls, audio device selection, sleep timer, bookmarks, and technical metadata inspection.
- **Streamer Tools**:
  - Sleep timer with configurable durations (15m, 30m, 45m, 60m).
  - OBS "Now Playing" text export (`now_playing.txt`) and stream markers timestamp log (`stream_timestamps.txt`).
  - Audio ducking support.
  - Quick file and folder navigation, search filter, and drag-and-drop loading.
- **Built-in Application Updater**: Check for and download the latest application updates directly from within the Help menu or automatically on startup.

## Requirements

- Windows 10 or later (64-bit recommended)
- Python 3.10+
- `wxPython >= 4.2.0`
- `mpv.dll` (included in repository)

## Getting Started

1. Clone the repository:
   ```bash
   git clone git@github-personal:muhamadalfian20892/Streamer.git
   cd Streamer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the application:
   ```bash
   python Streamer.py
   ```

## Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Space` | Play / Pause |
| `Ctrl + S` | Stop playback |
| `Ctrl + Left / Right` | Rewind / Fast-forward seek |
| `Up / Down` | Adjust volume up / down |
| `Ctrl + O` | Open music folder |
| `Ctrl + F` | Focus search filter |
| `Ctrl + P` | Open Settings dialog |
| `Ctrl + L` | Toggle repeat/loop mode |
| `Ctrl + H` | Toggle shuffle mode |
| `Ctrl + M` | Toggle mute |
| `Ctrl + Shift + L` | Switch interface language (ID / EN) |
| `F1` | Open User Guide dialog |

## License

MIT License.
