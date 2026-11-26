PANDUAN PENGGUNAAN STREAMER AUDIO PLAYER

Selamat datang di Streamer Audio Player. Aplikasi ini dirancang sebagai pemutar audio dan media yang ringan, cepat, serta ramah bagi pengguna pembaca layar seperti NVDA.

Semua tombol dan daftar kontrol dapat dioperasikan penuh menggunakan keyboard, dengan urutan fokus yang teratur dan label suara yang jelas.


1. DUA PILIHAN TAMPILAN: STANDARD MODE DAN ADVANCED MODE

Aplikasi ini menyediakan dua mode penggunaan yang dapat Anda pilih sesuai kebutuhan:

a. Standard Mode (Mode Standar)
Tampilan pemutar musik yang bersih, sederhana, dan fokus. Pada mode ini, antarmuka hanya menampilkan kendali pemutar standar, yaitu tombol Buka Folder, Putar, Jeda, Berhenti, Trek Sebelumnya, Trek Berikutnya, Penggeser Durasi, Penggeser Volume, Bisukan Suara, Ulangi Lagu, Putar Acak, Pilihan Perangkat Audio, dan Kotak Pencarian.
Mode ini sangat cocok untuk mendengarkan koleksi musik harian tanpa terganggu oleh menu alat siaran.

b. Advanced Mode (Mode Lanjutan)
Tampilan lengkap untuk kebutuhan live streaming dan pembuatan konten. Selain seluruh fungsi pemutar standar, mode ini membuka fitur tambahan seperti ekspor judul lagu ke now_playing.txt untuk OBS Studio, pencatat momen siaran (Stream Marker), audio ducking, penanda posisi audio (Bookmarks), dan efek audio tambahan.

Cara mengganti mode: Tekan Ctrl+P untuk membuka jendela Pengaturan, lalu pilih mode yang Anda inginkan pada menu "Mode Tampilan Aplikasi".


2. TATA LETAK DAN NAVIGASI APLIKASI

Untuk pengguna pembaca layar maupun pengguna visual, tata letak aplikasi disusun berurutan dari atas ke bawah:

- Bagian Atas (Navigasi): Tombol Buka Folder (Ctrl+O), Tombol Pengaturan (Ctrl+P), dan daftar riwayat folder yang pernah dibuka.
- Bagian Pencarian: Kotak pencarian cepat dan penyaring tampilan (pilihan untuk menampilkan Semua file, Hanya File audio/video, atau Hanya Folder).
- Bagian Tengah (Daftar File dan Penampil Video):
  * Sisi kiri adalah daftar file dan folder dalam direktori aktif.
  * Sisi kanan adalah panel video yang akan menampilkan gambar saat Anda memutar file video seperti MP4 atau MKV.
- Bagian Bawah (Indikator dan Kontrol Pemutaran):
  * Teks indikator durasi yang menampilkan waktu berjalan dan total durasi lagu.
  * Penggeser posisi lagu (Seek slider) untuk melompat ke detik tertentu.
  * Penggeser volume audio dengan batas hingga 150% beserta kotak edit input volume manual di sebelahnya (perubahan volume lewat kotak edit mengikuti durasi fading).
  * Baris tombol kendali: Mundur, Putar/Jeda, Berhenti, Maju, Trek Sebelumnya, Trek Berikutnya, Ulangi (Loop), Acak (Shuffle), dan Bisukan (Mute).
  * Menu pilihan Audio Device untuk memilih kartu suara atau perangkat keluaran audio yang aktif.


3. PANDUAN PENGGUNAAN FITUR

a. Membuka Folder dan Memilih Lagu
- Jalankan aplikasi Streamer.
- Tekan Ctrl+O atau klik tombol Buka Folder untuk memilih folder musik di komputer Anda.
- Gunakan tombol Panah Atas dan Panah Bawah untuk menjelajahi daftar lagu.
- Tekan Enter pada lagu untuk mulai memutar.
- Tekan Enter pada folder untuk masuk ke dalam folder tersebut.
- Tekan tombol Backspace untuk kembali ke folder sebelumnya (naik satu tingkat direktori). Bila Anda sudah berada di batas folder terluar, aplikasi akan memberikan pemberitahuan.
- Aplikasi mendukung berkas audio (MP3, WAV, FLAC, OGG, M4A, AAC, WMA, OPUS) dan berkas video (MP4, MKV, AVI, MOV, WMV, WEBM, MPG).

b. Kendali Pemutaran Musik
- Play dan Pause: Tekan tombol Spasi atau tombol Putar/Jeda.
- Stop: Menghentikan pemutaran lagu dan mengembalikan posisi ke awal.
- Loop: Tekan Ctrl+L untuk mengulang lagu yang sama terus-menerus. Pembaca layar akan mengumumkan "Loop Hidup" atau "Loop Mati".
- Shuffle: Memutar lagu dalam daftar secara acak.
- Pengaturan Volume: Tekan Ctrl+Panah Atas untuk menaikkan volume, dan Ctrl+Panah Bawah untuk menurunkannya. Anda juga dapat menggunakan slider volume atau mengetik angka volume langsung pada kotak edit di sebelah slider lalu tekan Enter agar volume berubah halus mengikuti durasi fading.
- Lompat Durasi: Tekan Ctrl+Panah Kiri untuk melompat mundur beberapa detik, dan Ctrl+Panah Kanan untuk melompat maju.

c. Pengaturan Audio dan Equalizer (Ctrl+P)
Di menu Pengaturan, Anda dapat mengatur:
- Preset Equalizer: Pilihan profil Flat (netral), Bass Boost (penguat bass), Treble Boost (penguat nada tinggi), atau Vocal (fokus kejelasan vokal).
- Normalisasi Audio: Menyamakan kenyaringan suara antar lagu secara otomatis agar volume terdengar merata.
- Suara Mono: Menggabungkan kanal stereo kiri dan kanan menjadi satu saluran mono.
- Audio Fading: Fitur peredupan suara halus saat mengganti lagu atau saat menekan jeda, sehingga suara tidak terpotong mendadak. Anda dapat mengatur durasi peredupan sesuai kenyamanan.

d. Fitur Khusus Streamer (Tersedia di Advanced Mode)
- Audio Ducking (Alt+D): Menurunkan volume musik latar secara instan saat Anda sedang berbicara, lalu tekan Alt+D kembali untuk mengembalikan volume musik ke tingkat semula.
- Soundboard (Alt+1 hingga Alt+9): Memutar efek suara pendek pada jalur audio terpisah tanpa menghentikan lagu utama yang sedang berjalan.
- Stream Marker (F9): Menuliskan waktu dan catatan momen ke file stream_timestamps.txt, berguna untuk menandai kejadian menarik selama siaran langsung.
- Integrasi OBS Studio: Aplikasi secara otomatis menulis nama trek yang sedang diputar ke file now_playing.txt sehingga dapat dijadikan sumber teks pada OBS Studio.

e. Pengatur Waktu Tidur (Sleep Timer)
Jika Anda suka mendengarkan musik menjelang istirahat, Anda dapat mengatur timer otomatis pada menu Pengaturan (Ctrl+P). Pilih durasi 15 menit, 30 menit, 45 menit, atau 60 menit. Musik akan berhenti sendiri begitu waktu habis.


4. AKSESIBILITAS DAN PEMBACA LAYAR (NVDA)

Aplikasi ini dibangun dengan perhatian penuh terhadap aksesibilitas:
- Seluruh tombol, kotak centang, penggeser angka, dan menu pilihan memiliki label nama yang terbaca oleh screen reader (SetName) serta teks petunjuk (tooltip).
- Anda dapat menekan Tab untuk maju ke elemen berikutnya dan Shift+Tab untuk mundur ke elemen sebelumnya.
- Tingkat Pengumuman Suara (Verbosity): Di menu Pengaturan, Anda dapat memilih antara Verbose (semua informasi volume dan durasi diumumkan), Minimal (hanya pengumuman penting), atau Silent (hening tanpa suara pengumuman tambahan).
- Sinyal Audio: Aplikasi membunyikan nada bip pendek saat kursor mencapai batas paling atas atau paling bawah daftar lagu.


5. DAFTAR LENGKAP TOMBOL PINTASAN (SHORTCUTS)

- Ctrl + O : Membuka folder musik baru
- Ctrl + P : Membuka jendela Pengaturan (Settings)
- Spasi : Putar atau Jeda (Play / Pause)
- Ctrl + Panah Atas : Menaikkan volume suara
- Ctrl + Panah Bawah : Menurunkan volume suara
- Ctrl + Panah Kanan : Melompat maju (durasi seek)
- Ctrl + Panah Kiri : Melompat mundur (durasi seek)
- Ctrl + L : Mengaktifkan atau mematikan pengulangan lagu (Loop)
- Ctrl + D : Menandai file sebagai lagu favorit (Pin)
- Backspace : Kembali ke folder di atasnya
- Enter : Memutar lagu terpilih atau membuka folder terpilih
- F5 : Menyegarkan isi daftar folder aktif
- Tab / Shift + Tab : Berpindah antar bagian antarmuka
- Alt + D : Menurunkan atau memulihkan volume musik latar (Ducking, Advanced Mode)
- F9 : Menyimpan tanda waktu momen siaran (Marker, Advanced Mode)
- Alt + 1 sampai 9 : Memutar efek suara soundboard (Advanced Mode)


Selamat mendengarkan musik dan menikmati siaran Anda!
