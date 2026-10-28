# VTUBE OS Feature Catalog and Delivery Roadmap

Catatan penting:
- Daftar di bawah ini adalah spesifikasi produk VTUBE OS yang lengkap.
- Tidak semua item harus dibuat dalam satu rilis. Semua fitur perlu dipilah berdasarkan prioritas, validasi perangkat, keamanan, dan kesiapan teknis.
- Repositori saat ini hanya berisi prototipe awal: desktop control center, avatar editor 2D, live pipeline FFmpeg, dan Android companion VTUBE Connect untuk kamera/mikrofon/screen sharing lokal.

## Status penerapan
- Implemented prototype: fitur yang sudah ada di repo saat ini
- In progress: sedang dikembangkan di roadmap aktif
- Planned: fitur yang direncanakan setelah MVP stabil
- Future / optional: fitur mayor yang membutuhkan riset, keamanan, atau integrasi pihak ketiga

---

## A. FITUR VTUBE OS

### 1. Desktop dan Antarmuka
- Desktop khusus VTUBE OS — Planned
- Dashboard utama — Implemented prototype
- Launcher aplikasi — Planned
- Taskbar dan panel notifikasi — Planned
- Tema terang dan gelap — Planned
- Kustomisasi wallpaper, ikon, warna, tampilan — Planned
- Pencarian aplikasi, file, pengaturan — Planned
- Pengelola file — Planned
- Pintasan keyboard — Planned
- Banyak jendela dan desktop virtual — Planned
- Pengaturan bahasa, waktu, jaringan, akun — Planned
- Pusat bantuan — Planned

### 2. Sistem Operasi dan Instalasi
- Berbasis Linux — Implemented via Debian Live build definition
- Bootable ISO — In progress
- Live USB — In progress
- Installer grafis — Planned
- Instalasi ke HDD dan SSD — Planned
- Dukungan BIOS dan UEFI — Planned
- Pengaturan partisi — Planned
- Dual boot — Planned
- Pemulihan sistem — Planned
- Pemeriksaan kompatibilitas perangkat — Planned
- Pengelolaan driver — Planned
- Pembaruan sistem — Planned
- Backup dan pemulihan konfigurasi — Planned

### 3. VTUBE Control Center
- Pusat kendali seluruh fitur VTUBE OS — Implemented prototype
- Pratinjau gameplay PC dan HP — In progress
- Pratinjau avatar — Implemented prototype
- Status kamera dan mikrofon — Implemented prototype
- Status koneksi HP — Implemented prototype
- Panel chat dan donasi — Implemented prototype
- Mixer audio — Planned
- Kontrol scene streaming — Implemented prototype
- Kontrol perekaman — Planned
- Status siaran langsung — Implemented prototype
- Statistik CPU, GPU, RAM, FPS, jaringan — Planned
- Panel yang bisa dikustomisasi — Planned
- Profil streaming per game — Planned

### 4. VTUBE Avatar Studio
- Membuat avatar VTuber — Implemented prototype (2D)
- Mengimpor dan mengekspor avatar — Implemented prototype (SVG/JSON)
- Dukungan avatar 2D dan 3D — Planned
- Dukungan Live2D dan VRM sesuai kompatibilitas — Planned
- Kustomisasi rambut, mata, wajah, pakaian, aksesori — Implemented prototype
- Pengaturan warna, tekstur, material — Planned
- Pengelolaan banyak avatar — Implemented prototype (local save/load)
- Pengaturan ekspresi wajah — Implemented prototype
- Animasi mulut — Planned
- Pengaturan gerakan kepala dan tubuh — Planned
- Hotkey ekspresi — Planned
- Emote dan animasi — Planned
- Pratinjau avatar — Implemented prototype
- Pengaturan pencahayaan avatar 3D — Planned
- Profil avatar untuk setiap scene — Planned

### 5. Face Tracking dan Motion Tracking
- Tracking wajah melalui webcam — Planned
- Tracking wajah melalui kamera HP — Planned
- Tracking mata dan kedipan — Planned
- Tracking arah kepala — Planned
- Tracking gerakan mulut — Planned
- Tracking ekspresi wajah jika didukung — Planned
- Kalibrasi wajah — Planned
- Pengaturan sensitivitas — Planned
- Pengaturan kehalusan gerakan — Planned
- Pengurangan gerakan tidak stabil — Planned
- Dukungan avatar 2D dan 3D yang kompatibel — Planned
- Indikator kualitas tracking — Planned
- Mode hemat sumber daya — Planned

### 6. Camera dan Webcam Studio
- Webcam bawaan laptop — Planned
- Webcam USB — Planned
- Kamera depan HP — Implemented prototype via VTUBE Connect
- Kamera belakang HP — Planned
- Pratinjau kamera — Implemented prototype
- Pengaturan resolusi dan FPS — Implemented prototype
- Pengaturan orientasi dan rotasi — Planned
- Fokus dan eksposur jika tersedia — Planned
- Rasio gambar — Planned
- Pemilihan kamera untuk tracking — Planned
- Pemilihan kamera untuk streaming — Planned
- Chroma key — Planned
- Profil kamera per scene — Planned
- Pemeriksaan masalah kamera — Planned

### 7. Microphone dan Audio Studio
- Mikrofon laptop — Planned
- Mikrofon USB — Planned
- Mikrofon headset — Planned
- Mikrofon HP — Implemented prototype
- Mikrofon eksternal yang terhubung ke HP — Planned
- Audio game PC — Planned
- Audio game HP jika dapat ditangkap — Planned
- Audio desktop — Planned
- Audio browser — Planned
- Audio TTS — Planned
- Audio notifikasi donasi — Planned
- Volume dan gain terpisah — Planned
- Mute dan unmute — Planned
- Input dan output audio — Planned
- Noise suppression — Planned
- Noise gate — Planned
- Compressor dan limiter — Planned
- Equalizer — Planned
- Monitoring audio — Planned
- Pengurangan gema — Planned
- Sinkronisasi audio dan video — Planned
- Pengaturan latensi — Planned
- Preset audio untuk gaming dan streaming — Planned

### 8. VTUBE Live Studio
- Membuat dan mengatur scene — Implemented prototype
- Transisi antar-scene — Planned
- Menambahkan avatar — Implemented prototype
- Menambahkan webcam — Planned
- Menangkap gameplay PC — Planned
- Menangkap layar HP — Implemented prototype
- Menangkap jendela aplikasi — Planned
- Menambahkan browser, gambar, video, teks — Planned
- Chat dan notifikasi donasi — Planned
- Mengatur posisi dan ukuran sumber — Planned
- Transparansi — Planned
- Mixer audio — Planned
- Chroma key — Planned
- Perekaman video — Planned
- Screenshot — Planned
- Replay buffer — Planned
- Virtual camera — Planned
- Resolusi dan FPS — Implemented prototype
- Bitrate — Implemented prototype
- Pratinjau sebelum siaran — Planned
- Pemantauan performa — Planned
- Integrasi OBS jika diperlukan — Planned

### 9. Chat Center
- Integrasi chat TikTok LIVE — Future
- Integrasi chat YouTube Live — Future
- Integrasi chat Twitch — Future
- Penggabungan chat platform — Future
- Overlay chat — Planned
- Ukuran dan warna — Planned
- Filter spam dan kata tertentu — Planned
- Moderasi sesuai izin platform — Future
- Penandaan pesan penting — Planned
- TTS pesan — Planned
- Volume TTS — Planned
- Riwayat chat — Future
- Notifikasi aktivitas penonton — Planned

### 10. Saweria dan Donation Center
- Integrasi Saweria sesuai metode yang tersedia — Future
- Notifikasi donasi — Implemented prototype
- Overlay donasi — Implemented prototype
- Animasi dan durasi notifikasi — Planned
- Batas minimum notifikasi — Planned
- TTS donasi — Planned
- Target donasi — Implemented prototype
- Tampilan progres target — Implemented prototype
- Riwayat donasi — Planned
- Media share jika didukung — Future
- Simulasi donasi untuk pengujian — Implemented prototype
- Dukungan layanan donasi lain — Future

### 11. Streaming Platform Center
- Pengelolaan profil streaming — Implemented prototype
- Integrasi TikTok LIVE — Future
- Integrasi YouTube Live — Future
- Integrasi Twitch — Future
- Platform lain — Future
- Pengaturan judul dan kategori — Planned
- Penyimpanan stream key aman — Planned
- Resolusi, FPS, bitrate — Implemented prototype
- Pemeriksaan koneksi sebelum siaran — Planned
- Status siaran langsung — Planned
- Pemantauan dropped frames — Planned
- Peringatan koneksi buruk — Planned
- Pengaturan audio dan video — Planned
- Banyak profil — Planned
- Multistream — Future

### 12. Overlay dan Asset Studio
- Editor overlay drag-and-drop — Planned
- Template layar mulai streaming — Planned
- Template layar istirahat — Planned
- Template layar penutupan — Planned
- Overlay game PC — Planned
- Overlay game HP — Planned
- Overlay avatar dan webcam — Planned
- Overlay chat dan donasi — Planned
- Widget status streaming — Planned
- Widget statistik — Planned
- Penambahan teks, gambar, video, animasi — Planned
- Transparansi, ukuran, posisi — Planned
- Font dan aset — Planned
- Pratinjau overlay — Implemented prototype
- Penyimpanan banyak tema — Planned
- Impor dan ekspor konfigurasi — Planned

### 13. Gaming dan Performance Center
- Peluncur game PC — Planned
- Profil per game — Planned
- Penangkapan gameplay — Planned
- Pengaturan audio game — Planned
- Overlay performa — Planned
- Statistik CPU, GPU, RAM, jaringan — Planned
- Pemantauan FPS — Planned
- Pengaturan penggunaan sumber daya — Planned
- Mode performa laptop low-end — Planned
- Mode hemat sumber daya — Planned
- Hotkey — Planned
- Dukungan gamepad — Planned
- Peringatan penggunaan sumber daya tinggi — Planned
- Profil ringan dan berat — Planned
- Mobile Gaming Mode — Planned

### 14. System Settings
- Jaringan — Planned
- Wi-Fi dan Ethernet — Planned
- Layar dan resolusi — Planned
- Audio — Planned
- Kamera — Planned
- Keyboard dan mouse — Planned
- Bahasa dan waktu — Planned
- Akun pengguna — Planned
- Notifikasi — Planned
- Tema — Planned
- Startup — Planned
- Aplikasi bawaan — Planned
- Penyimpanan — Planned
- Pembaruan — Planned
- Privasi — Planned
- Koneksi perangkat — Planned

### 15. Security dan Privacy Center
- Akun pengguna — Planned
- Hak akses — Planned
- Autentikasi perangkat — Planned
- Pairing perangkat aman — Planned
- Enkripsi komunikasi — Planned
- Penyimpanan token aman — Planned
- Izin kamera dan mikrofon — Implemented prototype
- Izin berbagi layar — Implemented prototype
- Izin kendali jarak jauh — Planned
- Daftar perangkat terhubung — Planned
- Pemutusan koneksi — Planned
- Pencabutan akses — Planned
- Riwayat sesi — Planned
- Notifikasi akses mencurigakan — Planned
- Penguncian sesi — Planned
- Remote access — Planned
- Firewall — Planned
- Pembaruan keamanan — Planned
- Pengiriman data diagnostik — Planned

### 16. Diagnostics dan Monitoring
- Status CPU, GPU, RAM, penyimpanan — Planned
- Status driver — Planned
- Suhu — Planned
- Jaringan — Planned
- FPS — Planned
- Bitrate dan dropped frames — Planned
- Latensi — Planned
- Status kamera dan mikrofon — Planned
- Status koneksi HP — Planned
- Pemeriksaan USB dan Wi‑Fi — Planned
- Layanan sistem — Planned
- Pengujian audio — Planned
- Pengujian kamera — Planned
- Log kesalahan — Planned
- Laporan diagnostik yang dapat ditinjau — Planned

### 17. Backup dan Synchronization Center
- Backup konfigurasi OS — Planned
- Backup avatar — Planned
- Backup scene — Planned
- Backup overlay — Planned
- Backup profil audio — Planned
- Backup profil streaming — Planned
- Backup konfigurasi perangkat — Planned
- Ekspor/import konfigurasi — Planned
- Pemulihan pengaturan — Planned
- Sinkronisasi antarperangkat — Future
- Pengelolaan versi konfigurasi — Planned
- Pemulihan setelah pembaruan — Planned

### 18. Plugin dan Extension Manager
- Daftar plugin — Planned
- Instalasi dan penghapusan plugin — Planned
- Pembaruan plugin — Planned
- Pemeriksaan kompatibilitas — Planned
- Informasi izin plugin — Planned
- Pengelolaan tema — Planned
- Paket overlay — Planned
- Paket avatar — Planned
- Integrasi aplikasi lain — Future
- Dokumentasi API — Planned
- SDK plugin — Future
- Pengelolaan versi — Planned
- Pemeriksaan integritas paket — Planned
- Peringatan plugin tidak dikenal — Planned

### 19. Developer Mode
- Terminal Linux — Planned
- Pengelolaan layanan sistem — Planned
- Log viewer — Planned
- Pemeriksaan konfigurasi — Planned
- Dokumentasi API lokal — Planned
- SDK plugin — Planned
- Alat pengujian integrasi — Planned
- Alat build ISO — Planned
- Alat build APK — Planned
- Pemeriksaan dependensi — Planned
- Pengujian kompatibilitas — Planned
- Pengelolaan versi kode sumber — Planned
- Ekspor laporan bug — Planned
- Lingkungan pengujian pembaruan — Planned

### 20. Update Center
- Pembaruan keamanan — Planned
- Pembaruan OS — Planned
- Pembaruan modul VTUBE — Planned
- Pembaruan VTUBE Connect — Planned
- Catatan perubahan — Planned
- Pemeriksaan kompatibilitas — Planned
- Pengunduhan pembaruan — Planned
- Verifikasi paket — Planned
- Pengaturan waktu instalasi — Planned
- Notifikasi pembaruan — Planned
- Penanganan kegagalan — Planned
- Pemulihan versi sebelumnya — Planned
- Saluran stabil dan pengujian — Planned

### 21. Feature Recommendation Center
- Usulan fitur baru — Planned
- Formulir ide dan penjelasan — Planned
- Kategori ide — Planned
- Lampiran gambar atau video — Planned
- Pencarian ide yang sudah ada — Planned
- Voting dan dukungan — Planned
- Pelacakan status ide — Planned
- Notifikasi perubahan status — Planned
- Permintaan informasi tambahan — Planned
- Kotak masuk rekomendasi — Planned
- Pencarian dan filter — Planned
- Catatan internal pengembang — Planned
- Penggabungan ide serupa — Planned
- Arsip dan ekspor — Planned
- Statistik ide populer — Planned
- Penjelasan alasan diterima/ditunda/ditolak — Planned

### 22. Feedback Center
- Feedback tampilan OS — Planned
- Feedback avatar — Planned
- Feedback tracking — Planned
- Feedback audio — Planned
- Feedback streaming — Planned
- Feedback koneksi HP — Planned
- Feedback Mobile Gaming — Planned
- Feedback instalasi — Planned
- Feedback performa — Planned
- Feedback dokumentasi — Planned
- Formulir penilaian opsional — Planned
- Kategori feedback — Planned
- Lampiran opsional — Planned
- Riwayat dan status feedback — Planned

### 23. Bug Reporter
- Pelaporan bug — Planned
- Modul bermasalah — Planned
- Informasi versi OS — Planned
- Langkah reproduksi — Planned
- Hasil yang diharapkan — Planned
- Hasil yang sebenarnya — Planned
- Tingkat keparahan — Planned
- Screenshot opsional — Planned
- Log diagnostik — Planned
- Status laporan — Planned
- Informasi perbaikan — Planned
- Catatan perubahan — Planned
- Perlindungan data pribadi — Planned

### 24. Community Hub dan Public Roadmap
- Daftar fitur yang direncanakan — Planned
- Daftar fitur yang sedang dikembangkan — Planned
- Daftar fitur yang sedang diuji — Planned
- Daftar fitur yang sudah dirilis — Planned
- Daftar fitur yang ditunda — Planned
- Voting komunitas — Planned
- Pengumuman pengembang — Planned
- Changelog — Planned
- Statistik rekomendasi — Planned
- Moderasi spam — Planned
- Dashboard pengembang — Planned
- Notifikasi fitur baru — Planned
- Sistem backend masukan internet — Future
- Penyimpanan draft lokal saat offline — Planned

### 25. Feature Development dan Delivery
- Meninjau permintaan pengguna — Planned
- Kelayakan teknis — Planned
- Menentukan prioritas — Planned
- Mengembangkan fitur — Planned
- Menguji fitur — Planned
- Memeriksa keamanan — Planned
- Memeriksa kompatibilitas — Planned
- Membuat paket rilis — Planned
- Menerbitkan pembaruan — Planned
- Menampilkan changelog — Planned
- Memberi notifikasi — Planned
- Mengumpulkan feedback setelah rilis — Planned

### 26. Mode Operasi VTUBE OS
- PC VTuber Mode — Planned
- Mobile Gaming Mode — Planned
- Webcam Mode — Planned
- Phone Microphone Mode — Planned
- Anywhere Remote Mode — Future
- Profil per game — Planned
- Profil avatar dan scene — Planned
- Profil audio dan kamera — Planned
- Penyimpanan konfigurasi mode — Planned
- Pergantian mode tanpa mengganti OS — Planned

### 27. Pengaturan Profil dan Otomatisasi
- Menyimpan profil setiap game — Planned
- Menyimpan scene streaming — Planned
- Konfigurasi avatar — Planned
- Konfigurasi kamera — Planned
- Profil mikrofon — Planned
- Konfigurasi Mobile Gaming — Planned
- Perangkat yang pernah dipasangkan — Planned
- Pemilihan profil manual — Planned
- Rekomendasi profil berdasarkan aplikasi — Planned
- Pemulihan konfigurasi setelah aplikasi ditutup — Planned
- Default saat boot — Planned
- Opsi menonaktifkan profil otomatis — Planned

### 28. Arsitektur dan Integrasi Internal
- Semua fitur desktop menjadi modul bawaan — Planned
- Dashboard terhubung ke modul internal — Planned
- Layanan koneksi perangkat — Planned
- Layanan audio dan kamera — Planned
- Layanan avatar dan tracking — Planned
- Layanan streaming — Planned
- Layanan notifikasi — Planned
- Layanan pembaruan — Planned
- Layanan diagnostik — Planned
- Integrasi VTUBE Connect — Implemented prototype
- Integrasi OBS jika diperlukan — Planned
- Integrasi platform streaming yang kompatibel — Future
- Backend komunitas — Future
- Pengujian integrasi antarmodul — Planned

---

## B. APLIKASI ANDROID VTUBE CONNECT

### 29. Fitur Utama VTUBE Connect
- Aplikasi Android untuk menghubungkan HP ke VTUBE OS — Implemented prototype source
- Pairing HP dan laptop — Implemented prototype
- Koneksi USB — Future
- Koneksi Wi‑Fi lokal — Implemented prototype
- Koneksi Anywhere melalui internet — Future
- Mengirim kamera HP ke laptop — Implemented prototype
- Mengirim mikrofon HP ke laptop — Implemented prototype
- Mengirim data face tracking — Future
- Mengirim tampilan layar HP — Implemented prototype
- Mengirim audio game jika didukung — Future
- Mengendalikan avatar — Future
- Mengganti ekspresi avatar — Future
- Mengaktifkan emote — Future
- Mengganti scene — Future
- Mengatur volume audio — Planned
- Mengendalikan perekaman — Planned
- Mengendalikan streaming jika didukung — Planned
- Mengirim file yang dipilih pengguna — Future
- Menampilkan status koneksi — Implemented prototype
- Menampilkan status kamera dan mikrofon — Implemented prototype
- Menampilkan status baterai jika tersedia — Planned
- Mengelola izin perangkat — Implemented prototype
- Memutuskan koneksi — Implemented prototype

### 30. Webcam Mode
- Menggunakan kamera depan HP — Implemented prototype
- Menggunakan kamera belakang HP — Planned
- Pratinjau kamera di laptop — Implemented prototype
- Resolusi — Planned
- FPS — Planned
- Orientasi — Planned
- Kualitas gambar — Planned
- Penggunaan kamera untuk face tracking — Future
- Penggunaan kamera untuk streaming — Implemented prototype
- Indikator kamera aktif — Planned
- Pemberitahuan ketika koneksi terputus — Planned

### 31. Microphone Mode
- Mikrofon bawaan HP — Implemented prototype
- Mikrofon eksternal yang kompatibel — Planned
- Pemilihan sumber mikrofon — Planned
- Gain dan volume — Planned
- Indikator level suara — Planned
- Pengujian mikrofon — Planned
- Pengurangan noise — Planned
- Kualitas audio — Planned
- Pemantauan koneksi — Planned
- Sinkronisasi audio dan video — Planned

### 32. Mobile Gaming Mode
- Menghubungkan HP saat bermain game ke laptop — Implemented prototype (screen share)
- Menampilkan layar HP di VTUBE OS — Implemented prototype
- Memilih USB atau Wi‑Fi — Future
- Resolusi tampilan — Planned
- FPS — Planned
- Kualitas gambar — Planned
- Menampilkan avatar di atas gameplay — Planned
- Menambahkan overlay chat — Planned
- Menampilkan notifikasi donasi — Planned
- Menjalankan TTS melalui VTUBE OS — Planned
- Menggunakan mikrofon HP — Implemented prototype
- Menggunakan mikrofon eksternal — Planned
- Menggunakan kamera HP secara terpisah — Planned
- Sinkronisasi audio dan video — Planned
- Memantau kualitas koneksi — Planned
- Menangani koneksi terputus — Planned
- Menyimpan profil per game — Planned

### 33. Remote Control
- Mengganti scene — Planned
- Mengubah ekspresi avatar — Planned
- Mengaktifkan emote — Planned
- Mengatur volume mikrofon — Planned
- Mengatur volume audio game — Planned
- Mengaktifkan atau menonaktifkan TTS — Planned
- Mengontrol perekaman — Planned
- Mengontrol streaming — Planned
- Melihat status siaran — Planned
- Melihat status kamera dan mikrofon — Planned
- Melihat notifikasi donasi — Planned
- Mengontrol fungsi dashboard yang diizinkan — Planned

### 34. USB Connection
- Pairing melalui USB — Future
- Transfer data kendali — Future
- Kamera HP jika didukung — Future
- Mikrofon HP jika didukung — Future
- Data tracking — Future
- Tampilan layar HP — Future
- Remote control — Future
- Transfer file — Future
- Pemantauan status koneksi — Future
- Penanganan koneksi terputus — Future

### 35. Wi‑Fi Connection
- Menemukan VTUBE OS di jaringan lokal — Implemented prototype via local IP
- Pairing menggunakan kode aman — Implemented prototype
- Kamera HP melalui jaringan — Implemented prototype
- Mikrofon HP melalui jaringan — Implemented prototype
- Pengiriman data tracking — Future
- Tampilan layar HP — Implemented prototype
- Remote control — Future
- Pengaturan kualitas video — Planned
- Pengaturan kualitas audio — Planned
- Pemantauan latensi — Planned
- Pemulihan koneksi — Planned

### 36. Anywhere Connection
- Pairing jarak jauh — Future
- Autentikasi perangkat — Future
- Enkripsi komunikasi — Future
- Remote control melalui internet — Future
- Mengubah scene dan ekspresi avatar — Future
- Mengatur volume — Future
- Melihat status streaming — Future
- Melihat status koneksi — Future
- Mengontrol perekaman — Future
- Mengontrol streaming jika didukung — Future
- Notifikasi perangkat terputus — Future
- Reconnect aman — Future
- Pengelolaan perangkat yang memiliki akses — Future
- Pencabutan akses jarak jauh — Future
- Riwayat sesi — Future

### 37. Pengaturan dan Status Perangkat
- Nama perangkat — Planned
- Status pairing — Implemented prototype
- Status koneksi — Implemented prototype
- Jenis koneksi aktif — Planned
- Kualitas jaringan jika tersedia — Planned
- Latensi — Planned
- Status kamera — Planned
- Status mikrofon — Planned
- Status berbagi layar — Planned
- Level baterai — Planned
- Suhu perangkat — Planned
- Resolusi dan FPS — Planned
- Kualitas audio — Planned
- Hemat baterai — Planned
- Daftar perangkat yang pernah dipasangkan — Planned
- Tombol memutuskan koneksi — Planned
- Pencabutan izin perangkat — Planned

### 38. Antarmuka VTUBE Connect di perangkat Android
- Halaman beranda — Implemented prototype UI
- Tombol hubungkan perangkat — Planned
- Daftar perangkat yang ditemukan — Planned
- Pairing menggunakan kode — Implemented prototype
- Halaman Webcam — Implemented prototype
- Halaman Microphone — Implemented prototype
- Halaman Mobile Gaming — Implemented prototype screen share UI
- Halaman Remote Control — Planned
- Halaman status koneksi — Planned
- Halaman pengaturan kualitas — Planned
- Halaman izin privasi — Implemented via Android OS permissions
- Riwayat koneksi — Planned
- Bantuan dan pemecahan masalah — Planned

---

## Prioritas rilis yang disarankan

### Rilis 1 — MVP / Foundational
- VTUBE OS desktop shell dasar
- VTUBE OS Control Center
- VTUBE Connect Android local pairing
- Kamera HP / mic HP / screen share
- Live preview dan FFmpeg ingest validation
- Live overlay avatar + donation panel
- Local stream output

### Rilis 2 — Studio Functional
- Avatar editor 2D lanjutan
- Scene editor dan multi-source layout
- Audio mixer dan device selection
- Multi-camera selection
- Live stream recording/replay
- Better UX and diagnostics

### Rilis 3 — Live VTuber Core
- Face tracking via webcam/phone camera
- Eye blink / head motion / mouth animation mapping
- Avatar 2D/3D rigging compatibility
- Stable local streaming pipeline
- Integration with streaming platform and chat overlays

### Rilis 4 — Production Hardening
- Security and privacy hardening
- Better pairing and encrypted tunnels
- Backup, restore, update center
- Installer and recovery flow
- Performance optimization for low-end hardware

### Rilis 5 — Community & Ecosystem
- Plugin manager
- Recommendation system
- Feedback and roadmap portal
- Community features and developer platform
- Extension ecosystem

---

## Prinsip pengembangan
- Mencapai kebutuhan pengguna secara bertahap
- Tidak menjanjikan semua fitur selesai dalam satu milestone
- Rekomendasi pengguna tidak boleh otomatis menjalankan kode pada perangkat pengembang
- Setiap fitur harus divalidasi di perangkat nyata dan jaringan yang aman sebelum dianggap siap untuk produksi
- Semua fitur berbasis internet harus mematuhi izin pengguna dan keamanan jaringan

---

## Ringkasan
Repo saat ini sudah berada pada fase prototype yang solid untuk:
- Android VTUBE Connect local network
- kamera HP / mic HP / screen share
- validasi FFmpeg ingest
- render overlay avatar + live stream build command
- desktop VTUBE control center

Yang belum menjadi produk final adalah:
- bootable OS installation
- real face tracking
- 3D avatar / Live2D / VRM support
- komunitas, integrasi platform, keamanan production-grade, dan sistem update lengkap

Implementasi semua fitur di atas sebaiknya dilakukan bertahap sesuai roadmap di atas, bukan dalam satu push besar.
