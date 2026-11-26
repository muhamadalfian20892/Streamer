STREAMER AUDIO PLAYER USER GUIDE

Welcome to Streamer Audio Player. This application is designed as a fast, accessible, and lightweight audio and media player for screen reader users and streaming creators.

Every control, button, and list is fully operable via keyboard, with logical focus order and explicit accessibility labels for screen readers like NVDA.


1. TWO DISPLAY MODES: STANDARD MODE AND ADVANCED MODE

You can switch between two modes based on your workflow needs:

a. Standard Mode
A clean, focused, distraction free audio player. In this mode, the interface only displays essential player controls: Open Folder, Play, Pause, Stop, Previous Track, Next Track, Seek Slider, Volume Slider, Mute, Loop, Shuffle, Audio Output Device selection, and Search.
This mode is ideal for daily music listening without streaming widgets getting in the way.

b. Advanced Mode
A comprehensive interface for live streaming and content creation. In addition to all standard player functions, this mode reveals advanced streamer tools: OBS now_playing.txt export, Stream Markers (timestamp logging), audio ducking, time bookmarks, equalizer presets, volume normalization, and mono downmix.

How to switch modes: Press Ctrl+P to open Settings, or use the View menu or the toggle button on the main window.


2. APPLICATION LAYOUT AND NAVIGATION

For both visual and screen reader users, the layout is organized logically from top to bottom:

- Top Bar (Navigation): Open Folder (Ctrl+O), Open File, Settings (Ctrl+P), and Recent Folders choice list.
- Search Section: Quick search box and View filter (All items, Files only, Folders only).
- Middle Section (File List and Video Panel):
  * Left pane: Interactive list of files and subfolders in the active directory.
  * Right pane: Video playback surface that displays visual content when playing video files (MP4, MKV, etc.).
- Bottom Section (Playback Controls):
  * Playback time button showing elapsed and total time (click to toggle remaining time).
  * Seek slider for jumping to specific track timestamps.
  * Audio volume slider (0 to 150%) and an adjacent manual volume edit field (entering a value fades smoothly over the configured fading duration).
  * Playback buttons: Previous, Rewind 5s, Play/Pause, Stop, Forward 5s, Next, Mute, Loop, and Shuffle.
  * Audio Device dropdown to select the active output sound card or headphones.
- Advanced Panel (Advanced Mode only): Stream Marker button, Bookmarks Manager, Audio Metadata Inspector, OBS export checkbox, Equalizer profile, Audio Normalization, and Mono Downmix.


3. FEATURE USAGE INSTRUCTIONS

a. Opening Folders and Selecting Tracks
- Launch Streamer.
- Press Ctrl+O or click Open Folder to select your music directory.
- Use Up Arrow and Down Arrow keys to browse tracks and folders.
- Press Enter or Space on a file to start playback.
- Press Enter on a folder to navigate inside it.
- Press Backspace to move up one folder level. The screen reader will announce when you reach the top directory boundary.
- Supported media formats include audio (MP3, WAV, FLAC, OGG, M4A, AAC, WMA, OPUS) and video (MP4, MKV, AVI, MOV, WMV, WEBM, MPG).

b. Playback Controls
- Play and Pause: Press Space or click Play/Pause button.
- Stop: Press Ctrl+S or click Stop to halt playback and reset time to 00:00.
- Loop: Press Ctrl+L to repeat the current track continuously.
- Shuffle: Toggle randomized track playback order.
- Volume: Press Ctrl+Up Arrow to raise volume, Ctrl+Down Arrow to lower volume, adjust the volume slider, or type a target percentage in the volume edit field next to the slider and press Enter to fade smoothly over the fading duration.
- Seek: Press Left Arrow / Right Arrow (or Ctrl+Left / Ctrl+Right) to jump backward or forward.
- Mute: Press Ctrl+M to silence audio sound instantly.

c. Audio and Equalizer Settings (Ctrl+P)
Under Settings, you can configure:
- Equalizer Profile: Flat, Bass Boost, Treble Boost, or Vocal clarity focus.
- Audio Normalization: Automatically balances loudness across quiet and loud tracks.
- Mono Audio Downmix: Combines stereo left and right channels to mono for single-ear streaming monitors.
- Audio Fading: Smooth volume fade-out when changing tracks or pausing, avoiding abrupt cuts.

d. Advanced Streamer Tools (Advanced Mode)
- Audio Ducking (Alt+D): Instantly lowers background music volume to 15% when speaking, then restores it when pressed again.
- Stream Marker (F9): Appends current time and date to stream_timestamps.txt to flag memorable moments.
- Bookmarks Manager: Save timestamps in long audio files and jump back to them with one click.
- OBS Studio Integration: Automatically writes currently playing song title to now_playing.txt for OBS text sources.
- Audio Metadata Inspector: Detailed technical readout of sample rate, channels, codec, duration, and tags.

e. Sleep Timer
If you listen to music before sleeping, configure the Sleep Timer in Settings (Ctrl+P) or from the Tools menu. Choose 15m, 30m, 45m, 60m, or custom duration. Audio smoothly fades out when the timer expires.


4. ACCESSIBILITY AND SCREEN READER (NVDA)

- 100% of controls, buttons, checkboxes, sliders, and menus have explicit accessible names (SetName) and tooltips.
- Press Tab to advance forward through controls and Shift+Tab to move backward.
- NVDA Speech Verbosity: In Settings, select Verbose (full spoken announcements), Minimal (important actions only), or Silent (mute automatic speech).
- Sound Cues: Distinct audio earcons play when reaching the top or bottom boundaries of the file list.
- Live Language Switching: Switch between English and Bahasa Indonesia on the fly without restarting.


5. COMPLETE SHORTCUTS REFERENCE

- Ctrl + O : Open folder
- Ctrl + Shift + O : Open single file
- Ctrl + P : Open Settings
- Space : Play / Pause
- Ctrl + S : Stop playback
- Ctrl + Up Arrow : Volume up
- Ctrl + Down Arrow : Volume down
- Ctrl + Right Arrow : Next track
- Ctrl + Left Arrow : Previous track
- Right Arrow : Seek forward 5 seconds
- Left Arrow : Seek backward 5 seconds
- Ctrl + L : Toggle loop mode
- Ctrl + M : Toggle mute
- Ctrl + D : Pin track to favorites
- Backspace : Go up one directory level
- Enter : Play selected track or open folder
- F1 : Open user guide
- F5 : Refresh active folder
- F9 : Place stream marker (Advanced Mode)
- Tab / Shift + Tab : Navigate between UI sections
