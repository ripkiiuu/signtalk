# MASTER TASK — Implementasi SIGNTALK PWA + ASL AI Coach

Kamu adalah coding agent utama untuk proyek SIGNTALK PKM-KC 2026. Kerjakan langsung pada workspace Windows:

`D:\ABOUT PRIMA\PKM\SIGNTALK`

## Tujuan produk
SIGNTALK adalah Progressive Web App (PWA) mobile-first, berbahasa Indonesia, untuk masyarakat Tuli Indonesia yang berminat mempelajari American Sign Language (ASL). SIGNTALK BUKAN penerjemah BISINDO, bukan penerjemah ASL ke bahasa Inggris secara bebas, dan bukan sistem yang menjamin kompetensi berbahasa ASL hanya dari landmark. ASL adalah bahasa tersendiri dengan unsur tangan dan penanda nonmanual yang relevan.

Alur belajar: Learn -> Watch -> Practice -> Real-Time Feedback -> Final Evaluation -> Progress.

7 fitur: (1) ASL Vocabulary Learning; (2) Common ASL Phrases; (3) AI Sign Recognition; (4) Real-Time Visual Feedback; (5) Interactive Mini Challenge; (6) Final Challenge Evaluation; (7) Learning Progress Dashboard.

Rancangan stack (adaptasikan dengan kode yang sudah ada): React + TypeScript + Vite + Tailwind CSS; manifest + service worker; kamera getUserMedia melalui HTTPS/localhost; MediaPipe Tasks Vision Hand/Face/Pose Landmarker; Python untuk preprocessing/training; model ringan (baseline dan, bila diperlukan, GRU/BiLSTM) yang dapat diekspor untuk TensorFlow.js atau ONNX Runtime Web; backend dan Firebase/Supabase hanya jika betul-betul dibutuhkan. Video pelajaran Common ASL Phrases di-embed dengan YouTube IFrame API resmi, bukan disalin/diunduh.

## Aturan operasi dan keselamatan kode
1. LANGKAH PERTAMA: audit workspace, status Git, file existing, package manager, framework, scripts, desain, struktur, dependensi, fitur yang sudah ada dan celah kebutuhan. Laporkan ringkas temuan dan rencana eksekusi, lalu implementasikan tanpa menunggu pertanyaan yang tidak perlu.
2. JANGAN menghapus, mengganti total, atau menimpa codebase/design yang sudah ada. Pertahankan pola, styling, routes, state, dan komponen eksisting. Jika sudah ada proyek React atau stack setara, lanjutkan proyek itu. Migrasi hanya jika terbukti perlu dan aman.
3. Cek `git status` sebelum perubahan. Jangan `git reset --hard`, `git clean -fd`, menghapus folder, memaksa push, mengirim kunci, atau melakukan tindakan destruktif. Jika ada perubahan pengguna yang belum committed, jangan hilangkan. Buat checkpoint/backup aman atau tanyakan persetujuan untuk perubahan berisiko.
4. Gunakan folder di workspace proyek, bukan membuat proyek paralel di lokasi lain. Usulkan struktur `src/` atau `frontend/`, `ai/`, `datasets/`, `models/`, `docs/` sesuai kenyataan repo. Jika data besar, gunakan `.gitignore`, metadata/manifest dan instruksi unduh; JANGAN commit dataset video/model besar ke Git.
5. Jangan memakai klaim evaluasi AI palsu. Bedakan `DEMO / MOCK`, `DETECTION ONLY`, `MODEL-BASED PREDICTION`, dan `VALIDATED FEEDBACK`. Kualitas koreksi belum terbukti sebelum benchmark dan validasi ahli ASL.
6. Tidak men-scrape/mengunduh video YouTube untuk training. YouTube hanya embed legal jika diizinkan; dataset penelitian harus mengikuti lisensi/term aslinya. Jangan auto-unduh >1 GB atau memasang layanan berbayar tanpa persetujuanku.
7. Pastikan user privacy: pemrosesan kamera lokal bila memungkinkan, consent kamera, tidak menyimpan atau mengirim video mentah tanpa persetujuan, jangan memasukkan secret ke frontend, sediakan `.env.example`.
8. Ikuti AGENTS.md yang ada; jika ingin memperbaruinya, gabungkan aturan, jangan menghapus instruksi pengguna.

## Tahap 0 — Audit dan rencana
- Jalankan inspeksi file serta test/build awal (jika tersedia).
- Catat dalam `docs/IMPLEMENTATION_PLAN.md` peta fitur, prioritas P0/P1/P2, kondisi saat ini, hambatan, urutan kerja, dan definisi selesai.
- Mulai implementasi P0 setelah audit. Bila dataset tak bisa diunduh/berizin/tersedia, lanjutkan fitur kamera dan UI dengan mode deteksi serta demo eksplisit; jangan memalsukan model.

## Tahap 1 — PWA dan pengalaman belajar
Implementasikan dan hubungkan tanpa merusak desain eksisting:
- Home Dashboard, kategori kosakata, halaman detail kosakata, Common ASL Phrases, detail ungkapan dengan YouTube embed, practice camera, result, learning progress, serta settings/privacy jika dibutuhkan.
- Materi bilingual: kata/ungkapan bahasa Inggris, penjelasan bahasa Indonesia, kategori, level, petunjuk belajar, attribution/source, dan status AI evaluable.
- Buat schema yang terstruktur, contoh minimal dan placeholder yang jelas jika video/label belum divalidasi; jangan memalsukan validasi ASL. Tidak semua phrase wajib punya AI challenge.
- PWA manifest, ikon yang layak, service worker untuk app shell / konten yang sah di-cache, installability, responsivitas, aksesibilitas keyboard, kontras, label, feedback teks+ikon+warna, loading/error/empty states. Video YouTube tidak dijanjikan offline.

## Tahap 2 — Real-time Computer Vision di browser
- Buat halaman webcam asli memakai browser permission APIs. Render kamera dan overlay landmark dengan koordinat yang terpetakan benar, termasuk mirroring, rotasi layar, scaling, dan resize.
- MediaPipe: prioritas tangan kanan-kiri (landmark), lalu pose dan wajah sebagai fitur tambahan dengan deteksi performance-aware; gunakan modul terpisah, throttling, requestAnimationFrame dan cleanup stream untuk mencegah kebocoran kamera / memory.
- Indikator `terdeteksi`, `tidak terlihat`, dan `belum bisa dinilai` harus dibedakan dari penilaian `benar/salah`. Jangan otomatis menandai semua titik hijau hanya karena landmark ditemukan. Tampilkan FPS/latency untuk debug, bukan wajib untuk pengguna.
- Sediakan panduan kamera (jarak, cahaya, kepala/dada/tangan terlihat). Tangani izin ditolak, kamera tak tersedia, browser tidak mendukung, dan perangkat lambat.

## Tahap 3 — Dataset ASL yang dapat direproduksi
- Teliti dokumentasi asli WLASL (https://github.com/dxli94/WLASL) dan ASL Citizen (https://www.microsoft.com/en-us/research/project/asl-citizen/), cek sumber video, lisensi, format, tautan unduh, kelas tersedia, serta persyaratan penggunaan akademik.
- Buat `docs/DATASET_GUIDE.md`: sumber resmi, atribusi, lisensi, cara mendapatkan data dengan izin, kebutuhan disk/memori, struktur data, dan batas penggunaan. Jangan mengunduh seluruh korpus besar tanpa konfirmasi.
- Buat utilitas Python `ai/scripts/inspect_dataset.py` untuk memeriksa metadata dan kelas (mis. 'sorry' jika memang tersedia). Buat skrip subset 5-10 kelas yang benar-benar ada dalam dataset, dengan mapping label yang reproducible.
- Data mentah hanya di `datasets/raw/` (di-ignore); hasil landmark di `datasets/processed/` (di-ignore). Dataset mencakup video, label, sumber, metadata signer bila tersedia. Catat data hilang/corrupt; jangan melabeli dari tebakan.
- Buat ekstraksi landmark tangan + optional pose/face via Python MediaPipe; normalisasi koordinat terhadap tubuh, sampling frame, missing-hand masks, handling panjang sequence. Simpan hasil/metadata dengan format jelas (npz/parquet/csv sesuai kebutuhan).

## Tahap 4 — Latih dan evaluasi model yang benar-benar bekerja
- Pertama buat baseline sederhana (mis. fitur hand landmark + classifier terukur), lalu bandingkan model temporal GRU/BiLSTM jika datanya mendukung. Hindari overengineering.
- Buat `ai/train.py`, `ai/evaluate.py`, `ai/export.py` (atau struktur ekuivalen), file requirements, seed reproducibility, label_map, metrics CSV/JSON, confusion matrix, loss curves opsional.
- Pisahkan train/val/test berdasarkan SIGNER/PARTISIPAN bila metadata memungkinkan; jika tidak, jelaskan keterbatasan secara jelas. Jangan klaim generalisasi dari random video split dengan signer bocor.
- Catat accuracy, macro precision, recall, F1, confusion matrix, inference latency, serta jumlah video yang benar-benar dipakai. Uji kasus `unknown/low confidence` dan jangan memaksa setiap input menjadi salah satu isyarat.
- Ekspor model + preprocessing config + label_map untuk inferensi browser (ONNX Runtime Web atau TensorFlow.js). Uji parity output Python dan browser pada sampel data, bila memungkinkan.
- Jangan mengaku model terlatih jika bobot/model belum berhasil dihasilkan dari training nyata.

## Tahap 5 — AI Coach: koreksi, bukan sekadar klasifikasi
- Pilih 1-3 isyarat pilot tervalidasi (mis. SORRY jika label dan referensinya tersedia). Buat rubric gerakan per isyarat: handshape, orientation, location relative to torso, movement path, penanda wajah/tubuh HANYA jika linguistik relevan. Status rubric: `draft`, `expert-reviewed`, `validated`.
- Untuk aspek statis, evaluasi fitur geometris seperti sudut jari, orientasi, jarak relatif tangan-dada. Untuk gerak dinamis, pakai urutan frame/time window dan bandingkan gerak (mis. DTW) serta klasifikasi model; jangan menghukum pengguna sebelum gerakan selesai.
- Bedakan `correct`, `needs-improvement`, `not-visible`, `insufficient-evidence`; gunakan ambang yang diuji dan smoothing/hysteresis agar overlay tak berkedip. Feedback merah/hijau hanya jika komponen tertentu memang dapat dinilai; selain itu kuning/abu-abu.
- Contoh pesan SORRY (jika sudah didukung rubric): "Dekatkan tangan ke dada", "Perhatikan bentuk jari", "Lengkapi gerakan melingkar"; semua petunjuk referensi harus dapat diubah lewat konfigurasi, bukan hardcode acak.
- Penilaian ekspresi wajah harus terkait isyarat yang relevan dan diuji bersama ahli ASL, bukan tebakan emosi berbasis ekspresi. Mungkin cukup 'wajah terlihat' sebagai MVP; jangan klaim evaluasi linguistik wajah bila belum ada.
- Result page menyajikan skor HANYA dengan formula nyata, data, limitations, dan disclaimer; jika belum valid gunakan label 'perkiraan/eksperimental' atau tidak tampilkan skor numerik.

## Tahap 6 — Integrasi akhir dan QA
- Semua rute berfungsi; koneksi lesson->video->challenge->camera->feedback->result->progress berjalan.
- Progres latihan disimpan secara lokal terlebih dahulu bila backend belum tersedia; fitur akun/cloud bersifat opsional, tidak boleh menghalangi MVP.
- Test komponen utama, typecheck, lint, build production, kamera permission states, PWA manifest/service worker, dan tes manual Chrome Android/Desktop jika device nyata tersedia. Catat hal yang tidak dapat diuji secara otomatis.
- Buat `README.md` yang jelas: instal dependensi, jalankan dev server, jalankan training pipeline, set environment, cara memperoleh dataset, cara convert model, jalankan tes, build PWA, troubleshooting Windows, status fitur.
- Buat `docs/STATUS.md` dengan tabel: implemented+tested / implemented but unverified / mock / blocked, artefak model dan metrik yang aktual, known issues, next tasks. Jangan mengklaim hal yang belum terbukti.

## Prioritas dan definisi selesai
P0: audit aman, PWA existing dapat run/build, materi + phrases + embed, live camera + landmark nyata + instruksi deteksi, alur challenge/result/progress, dokumentasi.
P1: pipeline dataset yang reproducible, baseline AI terlatih pada subset berizin, model web berjalan, klasifikasi live nyata dan hasil evaluasi.
P2: per-komponen coaching yang tervalidasi, wajah/tubuh linguistik, lebih banyak signs, akun online, peningkatan performa.

Bila dataset belum tersedia, selesaikan P0 + tooling P1; tulis batasan dan perintah/data yang dibutuhkan. Jangan menyamaratakan landmark detection dengan kemampuan menilai kebenaran ASL.

## Cara bekerja dan laporan
- Kerjakan file betulan, bukan sekadar memberikan saran/daftar tugas.
- Pecah perubahan menjadi langkah-langkah kecil, cek build/test setiap fase.
- Saat butuh keputusan yang berisiko (hapus file, overwrite desain, instal berbayar, unduh data besar, penggunaan dataset tanpa izin) berhenti pada aksi tersebut dan minta izin, sambil melanjutkan bagian yang aman.
- Pada akhir pekerjaan laporkan: file yang dibuat/diubah, perintah yang berhasil dijalankan, hasil build/test, status tiap fitur, model yang benar-benar terlatih, dataset yang benar-benar tersedia, serta blocker. Sertakan instruksi persis untuk menjalankan SIGNTALK di Windows.

MULAI SEKARANG DENGAN AUDIT REPO, LALU IMPLEMENTASIKAN P0 SECARA NYATA. Jangan buat proyek kedua jika kode SIGNTALK sudah ada.
