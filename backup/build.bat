@echo off
echo Building Streamer.py with Nuitka...

python -m nuitka --standalone --include-package=certifi --include-package-data=certifi --nofollow-import-to=PyQt5 --nofollow-import-to=torch --nofollow-import-to=PyQt6 --nofollow-import-to=PySide2 --nofollow-import-to=PySide6 --nofollow-import-to=qtconsole --nofollow-import-to=qtpy --nofollow-import-to=QtWebEngine --nofollow-import-to=google --nofollow-import-to=googleapiclient --nofollow-import-to=oauth2client --nofollow-import-to=yt_dlp.extractor.lazy_extractors --nofollow-import-to=unicodedata --output-dir=build_streamer Streamer.py

echo Build complete!
pause
