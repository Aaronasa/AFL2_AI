Aplikasi Deteksi Sampah Berbasis Android (Kotlin)

Ini adalah aplikasi Android berbasis Kotlin yang digunakan untuk mendeteksi dan mengklasifikasikan sampah menggunakan Machine Learning.
Aplikasi ini memanfaatkan model dari Teachable Machine dengan format .tflite yang dijalankan langsung di perangkat (offline).

Hasil deteksi sampah akan dibagi ke dalam:
3 kategori besar
9 kategori kecil (seperti plastik, kertas, kaca, logam, dll)

Aplikasi menyediakan dua mode penggunaan, yaitu Live Camera Detection dan Upload / Ambil Foto.

1. Library & Teknologi yang Digunakan

Aplikasi ini dibangun menggunakan teknologi Android modern dengan fokus pada performa dan kemudahan penggunaan.

Library & Tools

   Library / Teknologi	Kegunaan					Jenis
Kotlin		Bahasa pemrograman utama aplikasi Android	Built-in
Android Studio	IDE utama pengembangan aplikasi			Tool
Jetpack Compose	Membuat UI aplikasi (Menu, Kamera, Foto) 	Built-in
			secara declarative
CameraX		Mengakses kamera HP untuk live detection 	Dependency
			& ambil foto
TensorFlow Lite	Menjalankan model Machine Learning (.tflite)	Dependency
Teachable Machine	Platform training model klasifikasi sampah	External
AndroidX		Lifecycle, permission, camera provider		Built-in
Material 3		Komponen UI modern (Button, Text, Layout)	Built-in


Machine Learning Model
Format model: .tflite
File model: model_unquant.tflite
File label: labels.txt
Model diload dari folder assets
Inferensi berjalan offline (tanpa internet)

Alur klasifikasi:
Gambar di-resize ke 224 x 224
Normalisasi nilai pixel
Inferensi menggunakan TensorFlow Lite Interpreter
Ambil confidence tertinggi
Mapping label ke kategori sampah


2. IDE & Perangkat yang Digunakan
IDE:
Android Studio (disarankan versi terbaru)
Perangkat:
Laptop / PC
Smartphone Android
Kabel data USB
Rekomendasi:
Android minimal versi 8.0
Kamera HP berfungsi dengan baik


3. Cara Install & Menjalankan Aplikasi di HP
   A. Membuka Project di Android Studio
	1. Buka Android Studio
	2. Pilih Open
	3. Arahkan ke folder project aplikasi
	4. Tunggu proses Gradle Sync sampai selesai

   B. Mengaktifkan Developer Option di HP
	1. Masuk ke Settings / Pengaturan
	2. Pilih About Phone / Tentang Ponsel
	3. Cari Build Number
	4. Tap Build Number sebanyak 7 kali
	5. Akan muncul notifikasi “You are now a developer”

   C. Mengaktifkan USB Debugging
	1. Masuk ke Settings
 	2. Pilih Developer Options
 	3. Aktifkan USB Debugging
 	4. Sambungkan HP ke laptop menggunakan kabel data
 	5. Jika muncul pop-up di HP, pilih Allow / Izinkan

   D. Menjalankan Aplikasi ke HP
	1. Kembali ke Android Studio
 	2. Pada bagian Device / Media Run, pilih HP kamu
 	3. Klik tombol Run 
 	4. Tunggu proses build & instalasi
 	5. Jika berhasil, aplikasi akan otomatis terinstall dan terbuka di HP


4. Cara Menggunakan Aplikasi
Aplikasi memiliki 2 mode utama:

Mode 1: Live Camera Detection (Mode ini cocok untuk deteksi cepat secara langsung.)
   1. Buka aplikasi
   2. Pilih Live Camera Detection
   3. Kamera akan otomatis menyala
   4. Arahkan kamera ke objek atau sampah
   5. Aplikasi akan menampilkan:
	- Nama objek
	- Kategori sampah
	- Tingkat confidence
   6. Deteksi berjalan realtime selama objek berada dalam jangkauan kamera

Mode 2: Ambil Foto / Upload dari Galeri (Mode ini cocok untuk analisis yang lebih jelas dan detail.)
   1. Buka aplikasi
   2. Pilih Ambil Foto / Galeri
   3. User dapat:
	- Mengambil foto langsung dari kamera
	- Memilih foto dari galeri
   4. Setelah foto dipilih:
	- Gambar diproses
	- Hasil klasifikasi ditampilkan
   5. Hasil lebih fokus karena hanya satu objek

5. Kategori Sampah
Hasil prediksi dari model akan dipetakan ke kategori besar menggunakan sistem mapping, contohnya:
Plastik, kaca, logam → Mix Recycling
Kertas, kardus → Paper
Sampah sisa & organik → Residue

6. Catatan Tambahan
Akurasi dipengaruhi oleh pencahayaan
Objek sebaiknya terlihat jelas di kamera
Model Machine Learning menentukan hasil klasifikasi


Made By : 
Aaron Asa Soelistiono
Marcellino Indra Wijaya
Rinaldy Tanriady Tan

