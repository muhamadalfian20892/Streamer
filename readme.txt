Halo semua!

Ini aku ada bikinin aplikasi streamer audio (yang sekarang udah berevolusi jadi semacam Stream Deck) buat tugas kita. Aplikasi ini simpel banget dan sangat aksesibel buat kita yang pake screen reader kayak NVDA.

GAMBARAN TAMPILAN APLIKASI
Secara visual:
- Di bagian paling atas ada baris navigasi: tombol Open Folder, tombol Settings, dan dropdown buat milih Recent Folders (folder yang pernah dibuka sebelumnya).
- Di bawahnya ada kotak pencarian (Search) dan filter tampilan (buat misahin mana folder mana file).
- Di bagian tengah (paling besar), ada List View tempat semua daftar lagu atau file media kalian ditampilin. Di sebelahnya ada panel hitam kosong (panel ini buat nampung engine videonya, tapi karena kita fokus di audio, dia bakal hitam aja).
- Di bagian paling bawah ada indikator waktu durasi, slider volume, deretan tombol kontrol (Mundur 5s, Play/Pause, Maju 5s, dan toggle Loop), lalu yang terakhir ada pilihan Audio Device.

Secara aksesibilitas (Screen Reader):
- Kalian tinggal pakai tombol Tab dan Shift+Tab untuk lompat dari satu bagian ke bagian lainnya. Susunannya sangat rapi mulai dari tombol navigasi atas, kotak pencarian, daftar lagu utama, sampai ke tombol kontrol bawah.
- Di dalam daftar lagu, kalian tinggal pakai panah Atas/Bawah. NVDA bakal otomatis bacain nama lagu atau nama foldernya, dan kalau kalian cari lagu, jumlah hasilnya bakal dibacain.

CARA MENGGUNAKAN FITUR-FITUR UTAMA:

1. Buka Aplikasi & Pilih Lagu
- Jalanin aja aplikasinya (Streamer.exe). Kalo baru pertama kali buka, bakal ada panduan awal (Wizard) yang nyambut kalian.
- Pencet Ctrl+O atau klik tombol Open buat milih folder musik kalian.
- Kalau udah nemu lagu atau video yang mau diputar, pencet Enter atau Spasi.
- Buat masuk ke dalam folder, tekan Enter. Kalau mau kembali ke folder sebelumnya, tekan Backspace (NVDA bakal ngasih tau kalau kalian udah mentok di batas direktori).
- Aplikasi ini sekarang ngga cuma support MP3/WAV, tapi juga support format video kayak MP4, MKV, AVI, MPEG, dan lain-lain.

2. Kontrol Musik Dasar
- Play/Pause: Pencet Spasi atau tombol Play.
- Loop (Ulangin lagu): Pencet Ctrl+L. Nanti dia bakal bilang "Loop Hidup" atau "Loop Mati".
- Volume: Pencet Ctrl+Panah Atas biar kenceng, Ctrl+Panah Bawah biar pelan. Volumenya sekarang bisa nembus sampai 150%!
- Maju/Mundur: Pencet Ctrl+Panah kiri (Mundur 5 detik) atau Ctrl+Panah kanan (Maju 5 detik).
- Ganti Pitch & Speed: Tekan Ctrl+Shift+Panah kanan/Kiri buat cepetin atau lambatin lagu. Tekan Ctrl+Shift+Panah atas/Bawah buat ubah pitch (nada suara).

3. Fitur Stream Deck (Baru!)
- Aplikasi ini sekarang punya sistem "Global Hotkeys". Artinya, walaupun kalian lagi main game atau buka OBS (aplikasi ini lagi di-minimize), kalian tetep bisa ngejalanin fungsi-fungsi ini:
  * Audio Ducking: Tekan Alt+D dari mana aja, volume musik bakal langsung drop ke 15% (cocok buat pas kalian mau ngomong ke penonton). Tekan Alt+D lagi buat balikin volume ke normal.
  * Soundboard: Tekan Alt+1 sampai Alt+9 buat muterin sound effect. Sound effect ini diputar pakai engine terpisah, jadi bakal numpuk (overlapping) di atas lagu background kalian yang lagi jalan!
  * Stream Marker: Tekan F9 buat nulis timestamp waktu sekarang ke file stream_timestamps.txt. Berguna banget buat nandain momen lucu pas lagi live buat diedit nanti.

4. Integrasi OBS & Favorit
- OBS Export: Setiap kali lagu baru diputar, namanya otomatis ditulis ke file now_playing.txt. Kalian bisa masukin text file ini ke source OBS biar penonton tau lagu apa yang lagi muter.
- Favorit: Sorot file yang kalian suka, terus tekan Ctrl+D buat nge-pin (masukin ke daftar favorit).

5. Settings / Pengaturan (Ctrl+P)
Di menu Settings (tekan Ctrl+P), kalian bebas ngatur semuanya:
- Nyalain/matiin Auto-play (putar lagu selanjutnya otomatis).
- Ngatur efek "Audio Fading" (suara mengecil/membesar halus pas ganti lagu atau pas di-pause).
- Kalo kalian ngerasa fitur Stream Deck / Global Hotkeys itu kurang perlu, kalian bisa matiin dari Settings buat balikin aplikasi ini jadi versi standar yang ringan.
- Nyalain/matiin NVDA Verbose (kalo kalian gak mau NVDA ngoceh tiap kali ganti volume).

Kalo ada error atau apa, kabarin aku ya.

Tech stack: Python, wxPython, MPV, Keyboard.
Dibuat dengan vibe coders.
