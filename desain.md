# SIGNTALK — DESIGN SYSTEM, 3D EXPERIENCE & PRODUCT BLUEPRINT

> **Versi:** 1.0 — 8 November 2026  
> **Jenis:** Product requirements, UI/UX specification, 3D art direction, learning experience storyboard, accessible PWA architecture, AI integration contract, and acceptance criteria.  
> **Sumber kebutuhan:** `KONSEP AWAL SIGNTALK.pdf` dan dokumen konsep lanjutan SIGNTALK dari pemilik proyek.  
> **Status:** Spesifikasi implementasi — bukan bukti bahwa model AI, video demonstrasi, atau pengujian pengguna sudah tersedia.

---

## 00. PRODUCT NORTH STAR — SIGNTALK

**Nama:** SIGNTALK  
**Bentuk produk:** Progressive Web Application (PWA) pembelajaran American Sign Language (ASL).  
**Audiens:** masyarakat Tuli Indonesia yang *berminat* mempelajari ASL; kebutuhan aktual harus dikaji bersama calon pengguna.  
**Bahasa antarmuka awal:** Bahasa Indonesia; materi memuat kosakata/ungkapan ASL berlabel Inggris dan penjelasan Indonesia.  
**Alur inti:** **Learn → Watch → Practice → Real-Time Feedback → Final Evaluation → Progress**.  
**Posisi produk:** *Learn to sign. See your progress.* (tagline kreatif sementara, bukan janji kemampuan model).

### Signifikansi produk

SIGNTALK bukan penerjemah BISINDO→ASL, bukan penerjemah percakapan bebas, bukan pengganti guru ASL, dan bukan alat asesmen bahasa isyarat yang telah tervalidasi sebelum pengujian. SIGNTALK adalah lingkungan belajar terbimbing dengan demonstrasi visual, praktik kamera, pengenalan *kelas isyarat yang didukung*, evaluasi terukur, dan riwayat belajar.

### Tiga prioritas yang tidak bisa ditawar

1. **Pembelajaran benar:** materi, variasi isyarat, ekspresi dan tata bahasa yang relevan harus direview oleh penutur/pengajar ASL yang kompeten.
2. **Penilaian jujur:** landmark, klasifikasi, similarity, dan koreksi pedagogis adalah hal yang berbeda. Jangan tampilkan skor atau koreksi detail tanpa metodologi valid.
3. **Ramah perangkat dan aksesibel:** camera practice harus nyaman di iPhone, Android, dan laptop; 3D membantu penjelasan, bukan menghalangi fungsi inti.

### Definisi berhasil pada demonstrasi PKM-KC

Seorang pengguna dapat memilih satu materi yang memang didukung; menonton referensi valid; membuka kamera (setelah izin); melihat status tracking; melakukan praktik; mendapat hasil AI nyata untuk kelas yang didukung beserta indikator ketidakpastian; membaca feedback yang dapat dibenarkan; mengulang; dan melihat progres yang disimpan. Pada perangkat yang tidak mendukung WebGL, jalur belajar 2D tetap selesai.

---

## 01. CREATIVE DIRECTION — “THE LANGUAGE OF MOTION”

**Konsep:** ruang belajar digital yang hidup melalui gerakan tangan, kurva isyarat, dan objek 3D berkelas. Gunakan simbol komunikasi dalam bentuk kurva ruang yang menghubungkan adegan. Pengalaman ini **terinspirasi teknik scroll storytelling dan ruang 3D terhubung**, bukan menyalin karakter visual florist/medis dari proyek lain.

### Mood

- **Scientific clarity × human warmth:** modern, kredibel, optimistis, mudah didekati.
- **Kinetic but calm:** gerakan kamera purposeful, motion yang mengajari, bukan animasi acak.
- **Visual language-first:** tangan, gesture, simbol visual, ekspresi, label dan caption; tidak bergantung pada narasi audio.
- **Premium digital learning product:** terasa seperti hasil kolaborasi product designer, motion designer, dan praktisi aksesibilitas.

### Larangan visual (NO AI SLOP)

- Jangan gunakan “floating AI brain”, hologram acak, partikel neon tanpa makna, dashboard berisi kartu putih identik, glowing blobs, hero gradient generik, atau ikon tangan yang salah anatomi.
- Jangan memalsukan model tangan 3D photorealistic berisyarat yang belum diperiksa akurasinya.
- Jangan menyamakan gerakan avatar dekoratif dengan demonstrasi ASL yang benar.
- Jangan membuat 3D terasa dipaksakan pada halaman form atau camera feedback; halaman tersebut harus *utility-first*.
- Jangan membuat judul kecil, status sulit dibaca, hover-only navigation, ataupun puluhan video autoplay.
- Jangan menghilangkan fitur hanya untuk menyederhanakan layout.

### Arah palet (token awal — cek kontras secara nyata)

| Token | HEX | Penggunaan |
|---|---|---|
| `--canvas` | `#F7F8F6` | Latar aplikasi terang |
| `--surface` | `#FFFFFF` | Lembar baca / form |
| `--ink` | `#142D37` | Teks utama |
| `--muted` | `#566A71` | Teks sekunder yang tetap terbaca |
| `--navy` | `#153B4B` | Navigasi / tombol utama |
| `--teal` | `#167C83` | Interaksi dan progres (bukan status benar/salah) |
| `--mint` | `#DDF4ED` | Permukaan lembut |
| `--sky` | `#E5F3F8` | Layer visual dan konteks |
| `--peach` | `#F6E4DB` | Aksen hangat terbatas |
| `--line` | `#DCE6E5` | Separator |
| `--success` | `#176A4E` | Sesuai *jika* tervalidasi |
| `--caution` | `#9A5908` | Butuh pengulangan / tidak pasti |
| `--danger` | `#AE343F` | Kesalahan, bukan label 'isyarat buruk' |

**Catatan:** kontrol dan teks harus diverifikasi terhadap WCAG 2.2 AA; warna saja tidak cukup untuk menjelaskan hasil, tambahkan teks, bentuk, ikon, dan arahan tindakan. Kembangkan dark mode jika inti fungsional sudah stabil; jangan menjadikan tema gelap prasyarat demo AI.

### Tipografi

- Display/headline: **Manrope** atau **Plus Jakarta Sans** (satu keluarga utama; pertahankan rasa profesional).
- UI/body: **Inter** atau font sistem; maksimum dua keluarga total.
- H1 desktop: clamp(2.8rem, 5vw, 5rem), hanya untuk hero.
- Heading halaman aplikasi: 28–36 px, heading section 20–26 px.
- Body utama: 16–18 px; meta: minimal 13–14 px.
- Rasio line-height body 1.5–1.65; hindari all-caps panjang.
- Gunakan angka tabular untuk skor, progres, durasi tracking.

### Grid dan spacing

- Max-width editorial: 1200–1320 px; max-width bacaan: 760–860 px.
- Grid desktop 12 kolom; tablet 8; mobile 4. 
- Header 68–80 px; tidak menimpa hero.
- Sistem spacing 4/8/12/16/24/32/48/64/96.
- Border radius: 10–16 px UI, lebih besar hanya untuk surface konseptual; border tipis lebih utama dari shadow berat.
- Target sentuh minimal 44×44 CSS px; tampilkan fokus keyboard.
- Layar pendek, mode landscape, notch/safe-area iPhone diuji nyata.

---

## 02. TWO DIFFERENT VISUAL SYSTEMS, ONE PRODUCT

**A. Storytelling / discovery (3D-forward):** homepage, eksplorasi konsep, transisi ke kategori, “how it works”, model pedagogis tiga dimensi. Boleh menghadirkan adegan 3D kaya, kamera yang bergerak mengikuti scroll, foreground editorial, dan interaksi objek.

**B. Learning workspace (2D-first with purposeful 3D):** materi, detail ungkapan, praktik kamera, Mini Challenge, final evaluation, dashboard progres. Prioritaskan materi, pemutar video, form, feedback, data; 3D diintegrasikan hanya untuk analisis/sudut anatomi tangan dan orientasi bila akurat.

**Jangan menjadikan Canvas 3D global permanen** yang terus berjalan ketika kamera dan model inferensi aktif. Matikan/unmount scene dekoratif saat masuk ke kamera untuk mengurangi GPU contention; bila ada visualisasi tangan 3D di practice, jadikan *render-on-demand* dan turunkan kualitas sesuai profil perangkat.

---

## 03. USER JOURNEYS & INFORMATION ARCHITECTURE

### Pengunjung tanpa akun

Beranda → Jelajahi Materi → Kosakata/Frasa → Detail (judul EN, arti ID, konteks, video) → Latihan Preview → Registrasi opsional saat perlu menyimpan progres.

### Pengguna belajar

Beranda/Dasbor → Continue Learning → Learn → Watch → Practice setup → Camera preview → Mini Challenge → Feedback → Final Evaluation → Save Progress → Next Lesson.

### Konten admin/reviewer (akses terpisah bila backend tersedia)

Login authorized → Kelola materi → Tambah/ubah referensi video → Tandai `draft`/`needs_review`/`approved` → Set ketersediaan kelas AI → Publikasi konten setelah validasi ASL. Jangan memajang semua kosakata sebagai AI-supported.

### Navigasi

- **Publik:** Beranda, Belajar ASL, Ungkapan Umum, Cara Kerja, Tentang/Riset, Masuk/Progres.
- **Sesudah login:** Beranda Belajar, Materi, Mini Challenge, Progres, Pengaturan.
- **Mobile:** bottom navigation hanya untuk 4–5 tujuan terpenting; akses halaman sekunder via menu.
- **Practice:** mode fokus dengan exit, langkah, status kamera, referensi, feedback; jangan header promosi besar.

### Route yang direkomendasikan (sesuaikan implementasi)

| Route | Fungsi |
|---|---|
| `/` | 3D storytelling homepage |
| `/learn` | Eksplorasi kategori dan materi |
| `/learn/:slug` | Detail kosakata |
| `/phrases` | Common ASL Phrases |
| `/phrases/:slug` | Detail frasa, embed YouTube, konteks |
| `/practice/:lessonId` | Persiapan kamera + tracking + latihan |
| `/challenge/:lessonId/result/:attemptId` | Evaluasi akhir attempt |
| `/progress` | Perkembangan pengguna |
| `/account` | Akun/preferensi/privasi |
| `/about` | Metode, batasan, tim, kredibilitas |
| `/review` | Admin/reviewer (jika diimplementasikan) |

---

## 04. SIGNATURE 3D STORYBOARD — HOMEPAGE

**Teknik wajib:** Three.js + React Three Fiber (`@react-three/fiber`) dengan `@react-three/drei` sesuai kompatibilitas versi; kamera 3D nyata, objek nyata, bukan gambar 2D sekadar diberi transform CSS. Animasi scroll **boleh** memakai GSAP + ScrollTrigger, atau sistem `useScroll`/timeline serupa jika terbukti lebih stabil. Gunakan satu *story stage* dengan adegan modular; jangan membuat satu Canvas baru untuk setiap section tanpa alasan.

**Aesthetic treatment:** low-poly/soft-sculpture dimensional objects berkualitas tinggi, detail tangan anatomi yang ditinjau ahli, material matte-ceramic dan satin, pencahayaan studio, contact shadow halus; bukan model “AI 3D asset dump”. Kamera isometrik/orthographic 3/4 boleh digunakan untuk diagram pendidikan, dengan easing dan gerak terbatas.

### SCENE 00 — The Opening Gesture (hero)

- Latar bersih dengan visual *kinetic ribbon* yang membentuk kurva seperti aliran komunikasi (abstrak, tidak berpura-pura sebagai isyarat ASL).
- Satu tangan 3D **netral** atau abstraksi bentuk telapak, pose tanpa makna linguistik tertentu, menjadi pusat perhatian.
- Headline: **“Belajar bahasa isyarat, lewat gerakanmu sendiri.”**
- Subhead: “Pelajari ASL melalui demonstrasi visual, latihan kamera, dan evaluasi AI untuk materi yang didukung.”
- CTA utama “Mulai belajar”; CTA kedua “Lihat cara kerja”.
- Pada 1–2 scroll pertama, kamera melakukan pendekatan halus ke tangan, tidak menutupi CTA.
- Tangan tidak melakukan ASL tertentu kecuali pose, handshape dan konteksnya telah divalidasi.
- Header tidak overlap, state sticky muncul setelah melewati area hero.

### SCENE 01 — Learn: Vocabulary Universe

- Kamera bergeser ke ruang 3D miniatur bertajuk “Alphabet / Numbers / Greetings / Family” berupa blok/kartu konsep yang tersusun dalam ruang.
- Setiap item klik/tap menuju kategori nyata; objek 3D dan tombol DOM memiliki aksi yang sama.
- Pilihan kategori yang belum ada materi terverifikasi diberi label *segera hadir* / tidak dipublikasikan, bukan kartu link mati.
- Transisi kamera horizontal lembut mengikuti scroll; satu objek aktif, yang lain redup visualnya.

### SCENE 02 — Watch: Demonstration Studio

- Studio virtual kecil dengan sebuah panel video **DOM asli**, bukan video YouTube dijadikan tekstur 3D yang tidak aksesibel.
- Kamera 3D bergerak mendekati panel, lalu video/label muncul sebagai DOM overlay yang dapat dipause, diakses keyboard, dengan konteks/arti.
- Ilustrasi sudut pandang tangan dapat diputar hanya jika asset rig tervalidasi untuk isyarat tersebut.
- CTA “Lihat materi ASL”.

### SCENE 03 — Practice: Landmark Theater

- Demo konseptual alur kamera → hand landmarks → model AI menggunakan *illustrative wireframe 3D*. Ini adalah visualisasi mekanisme, **bukan kamera pengunjung diam-diam**.
- Landmark 21 titik/tangan dapat ditunjukkan pada model demonstrasi buatan. Jelaskan bahwa titik merupakan estimasi pelacak tangan, bukan jawaban benar/salah.
- Jika model contoh belum tersedia, tampilkan label “Simulasi alur teknologi” pada bagian edukasi ini; jangan menampilkan nilai prediksi palsu.
- CTA “Coba latihan” membuka izin kamera pada halaman praktik, bukan dari scroll landing.

### SCENE 04 — Feedback: See What to Improve

- Tampilan edukatif dua panel: contoh berlabel komponen isyarat vs indikator kualitas tracking; warna dan teks saling melengkapi.
- Kamera menjauh ke komposisi yang memperlihatkan **empat kriteria**: handshape, position, orientation, movement. Face/pose hanya jika konten tersebut memang memerlukannya.
- Konten menunjukkan *mekanisme konseptual*, bukan klaim model sudah dapat mengoreksi seluruh fitur secara akurat.
- Contoh UI: “Tangan terdeteksi”, “Orientasi belum dapat dinilai”, “Coba posisikan tangan lebih terang”.

### SCENE 05 — Growth: Learning Progress

- Jalur komunikasi 3D berubah menjadi *learning path* visual, berakhir pada panel progres nyata dari pengguna bila login, atau contoh struktural berlabel jelas jika belum login.
- Visual 3D rendah intensitas; grafik/progres tetap menggunakan HTML/SVG yang bisa diakses dan diperbesar.
- CTA penutup: “Mulai perjalanan SIGNTALK”.

### Cinematic scroll contract

- Story memiliki 6 beat dengan satu alur kamera eksplisit `{position, target, zoom/fov, activeScene, opacity}` per beat; interpolasi halus berdasarkan normalized scroll progress.
- One scroll = temporal storytelling, **bukan** memaksa pengguna menunggu berpuluh-puluh viewport hanya untuk menuju materi.
- Setiap section punya heading HTML dan tombol yang berfungsi.
- Scene tidak boleh sekadar berubah CSS opacity sementara kamera dan objek statis. Saat QA, buktikan kamera dan world coordinates berubah.
- Scroll idle: hibernasi render bila memungkinkan (`frameloop="demand"`/invalidation sesuai kebutuhan).
- Intro animasi sekali, bukan loop panjang. `prefers-reduced-motion`: hentikan camera travel, tampilkan ringkasan statis berurutan.
- Fallback 2D: ilustrasi dan konten DOM yang **desainnya setara**, tidak menampilkan error debug “3D tidak tersedia” secara kasar kepada pengguna.
- Semua action, informasi, dan harga (tidak relevan di sini) tetap dapat diakses tanpa 3D.

---

## 05. THREE.JS EXPERIENCE INSIDE LEARNING

### 3D Hand Explorer (educational feature)

Gunakan **model tangan rigged dengan anatomi masuk akal** yang sah dipakai dan memiliki atribusi/lisensi terdokumentasi; bila belum ada aset, buat *low-poly hand skeleton* untuk memahami orientasi, dengan label **“Model ilustratif”**. Tidak boleh memalsukan demonstrasi ASL dengan pose prosedural yang tidak tervalidasi.

Fungsi opsional yang berharga:
- Putar 360° menggunakan pointer/touch dan tombol rotasi kiri/kanan; tombol “Reset view”.
- Pilih sisi tangan (jika relevan), tampilan depan/samping, fokus pada telapak/jari.
- Overlay anatomi titik sendi dengan tooltip nama; tidak menyebut “benar” secara otomatis.
- Mode “compare” hanya setelah implementasi mapping koordinat, normalisasi handedness/mirroring, referensi tervalidasi dan evaluasi yang teruji.
- Konten materi inti tetap pada video demonstrasi manusia yang valid.

### Bukan satu hal yang sama

| Elemen | Definisi |
|---|---|
| Decorative 3D | Identitas visual/storytelling, tidak menilai pengguna |
| 3D instructional hand | Ilustrasi posisi/orientasi, bukan bukti ASL benar |
| Webcam overlay | Visualisasi landmark hasil deteksi perangkat |
| Sign recognition model | Memilih salah satu kelas yang didukung / tidak yakin |
| Assessment model | Memberikan feedback terukur pada komponen yang tervalidasi |

---

## 06. PAGE-BY-PAGE WIREFRAME & UX REQUIREMENTS

### A. Beranda (`/`)

1. Header fixed/sticky yang tidak menabrak hero, logo SIGNTALK, navigasi, CTA.
2. Hero 3D dengan headline dan visual yang seimbang (mobile mendahulukan CTA).
3. 3D journey lima tahap dari belajar ke progres.
4. Kategori terpilih dengan materi nyata, bukan kartu dummy.
5. Bagian “Bagaimana SIGNTALK bekerja” menjelaskan secara jujur status AI.
6. Bagian validasi/pengujian (hanya angka yang benar-benar ada).
7. CTA & footer: kontak tim, kebijakan kamera, batasan, sumber ASL.

### B. Katalog Vocabulary (`/learn`)

- Kategori: Alphabet/Fingerspelling, Numbers, Greetings, Family, Food & Drinks, Daily Activities, Emotions & Feelings.
- Search di judul Inggris/arti Indonesia, filter kategori, tingkat kesulitan, ketersediaan latihan AI.
- Lesson card: ikon/foto sah, title EN, arti ID, level, durasi **hanya jika diukur**, label **“Latihan kamera tersedia”** atau **“Materi saja”**.
- Jangan mengklaim 20–30 kelas sudah berjalan jika belum ada model.
- Empty state dan skeleton yang dapat dibaca, akses keyboard.

### C. Detail vocabulary (`/learn/:slug`)

- Breadcrumb, title Inggris + arti Indonesia, konteks yang valid.
- Video demonstrasi ASL melalui embed resmi/sumber berlisensi.
- Instruksi observasi: bentuk tangan, orientasi, gerak, ekspresi bila relevan.
- 3D Explorer opsional untuk sudut pandang; jangan mengubah tangan 3D menjadi satu-satunya sumber instruksi.
- “Mulai latihan” aktif hanya untuk kelas AI-supported; jika tidak ada: “Lihat latihan tanpa penilaian AI” dengan status yang jujur.
- Navigasi materi sebelumnya/berikutnya, simpan progres baca.

### D. Common ASL Phrases (`/phrases` dan `/phrases/:slug`)

- Phrase title EN + penjelasan ID, konteks pemakaian.
- Pemutar YouTube resmi; tidak mengunduh ulang materi tanpa izin.
- Tandai konten `draft`/`reviewed`/`approved`, sumber dan tanggal review.
- Mini Challenge untuk frasa hanya jika model kelas frasa terisolasi didukung; jika tidak, sediakan latihan mandiri tanpa angka penilaian.
- Tegaskan bahwa tata bahasa ASL tidak identik dengan urutan kata Inggris.

### E. Camera setup (`/practice/:lessonId` — preparation)

- Preflight jelas: kamera disarankan, pencahayaan, posisi seluruh tangan, jarak yang sesuai, pakaian/latar kontras, privasi.
- Minta izin kamera hanya setelah user menekan “Aktifkan kamera”.
- Video `<video playsinline muted>` untuk preview lokal dan canvas overlay HTML 2D ringan.
- Tambahkan toggle mirror preview, tetapi **jangan** mengubah handedness atau data klasifikasi tanpa transform terkoordinasi.
- Indikator “Kamera siap / belum diizinkan / tidak ditemukan / landmark tangan belum terdeteksi”.
- Preferensi kamera depan/belakang apabila perangkat mendukung; error dan retry.
- Jika iOS Safari/PWA membatasi frame processing, tampilkan opsi browser biasa/desktop dan petunjuk kompatibilitas.

### F. Interactive Practice (real-time)

**Desain desktop:** 60% kamera, 40% demonstration/instructions + feedback; **mobile:** camera panel di atas, instruksi dan feedback stabil di bawah, action utama di zona ibu jari.

- Region video: frame preview, 2D landmark overlay hasil inferensi, *optional* viewport 3D terpisah mode manual bila perangkat kuat.
- Header: nama isyarat, langkah 2/4, status “Live tracking”, tombol keluar.
- Live status: `Tangan belum terlihat` / `Terdeteksi` / `Kualitas tracking rendah` / `Siap mencoba`.
- Jika model klasifikasi siap: nama kelas diduga, confidence yang terkalibrasi bila tersedia, serta label ketidakpastian.
- Jika evaluator atribut tidak tersedia: tampilkan **“Evaluasi komponen belum tersedia”**, bukan merah otomatis.
- Real-time feedback dalam kalimat singkat yang bisa ditindaklanjuti: “Gerakkan tangan lebih dekat ke tengah frame” (berasal dari visibility), bukan “jari salah” tanpa evaluator.
- Beri opsi Pause, Ulangi, Lihat contoh, Selesaikan sesi.
- Jangan unggah raw video, gambar wajah, landmark biometric ke backend tanpa dasar, persetujuan eksplisit dan penjelasan retensi.

### G. Final Evaluation (`/challenge/:id/result/:attemptId`)

- Top summary: nama materi, tanggal, status hasil (`Recognized`, `Uncertain`, `No valid capture`); jangan hanya “berhasil/gagal”.
- Skor 0–100 **hanya** bila ada formula yang terdokumentasi, dikalibrasi, dan teruji; berbeda dari probabilitas klasifikasi.
- Breakdown untuk handshape/position/palm orientation/movement/facial marker/pose hanya jika evaluator masing-masing tersedia; yang lain `Not assessed`.
- Tampilkan *evidence limits*: “Hasil adalah estimasi dari model prototipe, dapat berbeda antar-pengguna.”
- Tindakan jelas: Coba Lagi, Kembali ke Video, Materi Berikut, Simpan Progres.
- Jika video tidak disimpan, jangan tampilkan tombol play replay hasil rekaman.

### H. Learning Progress (`/progress`)

- Ringkasan: materi selesai, kelas AI pernah dicoba, attempts, perbaikan sesi demi sesi jika skor valid.
- Progress per kategori, riwayat latihan, state supported/unsupported, saran lesson berbasis rule sederhana jika belum ada recommendation engine.
- Tidak mengarang streak atau peningkatan skill dari data minim.
- Data lokal saat offline dan sinkronisasi jika backend aktif; perjelas status sinkronisasi.
- Pengguna bisa menghapus riwayat sesuai kebijakan.

### I. About / Research

- Apa yang dilatih SIGNTALK, apa yang belum bisa dilakukan, sumber pengajaran, konteks PKM-KC, tim, prosedur penelitian, kebijakan data, batasan model.
- Konten bisa diakses tanpa 3D.

### J. Content reviewer/admin (fase lanjutan)

- CRUD kategori, kosakata, frasa, sumber video resmi, tag linguistik, level kesulitan, class label AI, ketersediaan evaluator.
- Workflow review berstatus `draft -> expert_review -> approved -> published`; publik hanya mengambil konten approved jika kebijakan rilis menuntut demikian.
- Pencatatan nama/afiliasi reviewer hanya jika disetujui; jangan mengarang validasi ahli.

---

## 07. LEARNING SYSTEM CONTENT CONTRACT

Setiap materi memiliki field:

```text
Lesson {
  id: string; slug: string; type: 'vocabulary' | 'phrase';
  categoryId: string; level: 'beginner' | 'intermediate' | 'advanced';
  englishText: string; indonesianMeaning: string;
  usageContextId: string; observationPoints: string[];
  sourceVideoUrl?: string; videoPlatform?: 'youtube' | 'licensed-hosted';
  imageUrl?: string; attribution?: string; licenseInfo?: string;
  aiClassId?: string;
  aiSupportStatus: 'not_supported' | 'planned' | 'available' | 'validated';
  assessmentComponents: Array<'handshape'|'location'|'orientation'|'movement'|'face'|'pose'>;
  reviewStatus: 'draft' | 'in_review' | 'approved';
  reviewerEvidence?: string; updatedAt: string;
}
```

Field ini adalah kontrak awal, bukan bukti bahwa data yang dimaksud telah dikumpulkan. **Jangan mengisi materi dengan gestur ASL buatan berdasarkan tebakan.** Contoh wireframe boleh memakai label materi tanpa aksi final; data pelajaran yang dipublikasikan harus memiliki sumber terpercaya atau validasi kompeten.

### Sumber demo dan dataset adalah entitas yang berbeda

- YouTube embed resmi = **referensi menonton**, tunduk pada hak dan kebijakan platform.
- Dataset model = **izin penggunaan untuk training**, label berkualitas, variasi subjek, metadata, evaluasi terpisah.
- Tidak boleh mengasumsikan video YouTube boleh diekstrak menjadi dataset AI.

---

## 08. CAMERA + AI ARCHITECTURE — TECHNICAL TRUTH

### Alur inferensi yang direkomendasikan

```text
User grants camera permission (HTTPS)
  -> HTMLVideoElement / local MediaStream
  -> Vision task(s) for hand landmarks, optionally face/pose
  -> normalize coordinates, handedness, scale, rotation, temporal features
  -> sequence window for the currently selected supported class(es)
  -> actual trained classifier (candidate BiLSTM / other validated baseline)
  -> calibrated class result or 'uncertain/not supported'
  -> independent validated assessment module for specific attributes (if any)
  -> readable feedback and a stored attempt summary (with consent)
```

**MediaPipe ≠ ASL recognition.** Hand Landmarker menyediakan 21 landmark per tangan; Face/Pose membutuhkan pemrosesan tambahan. BiLSTM hanyalah kandidat model—pemilihan arsitektur harus didasarkan pada data, baseline, dan performa terhadap penanda tangan yang belum terlihat sebelumnya.

### Engine separation

- `CameraSession` mengelola permission, lifecycle, `getUserMedia`, stop tracks saat exit/hidden.
- `LandmarkEngine` menangani MediaPipe; enabled modules per lesson, timestamps, quality, dropped frames; pertimbangkan Worker/OffscreenCanvas setelah memeriksa dukungan browser.
- `FeaturePipeline` normalisasi dan windowing konsisten training/inference; versioned contract.
- `SignClassifier` load model nyata; interface predictable `load`, `predict`, `dispose`, `supportedLabels`.
- `FeedbackEngine` memakai evaluator **yang sudah diimplementasi**; kalau tidak ada, hanya memberi tracking guidance, tidak mengklaim koreksi ASL.
- `AttemptRepository` menyimpan ringkasan sesi yang disetujui user.
- `ThreeScene` terpisah dari vision stack; jangan menggambar 3D berat pada camera path default.

### Contoh API respons aplikasi (bukan hasil model palsu)

```json
{
  "lessonId": "example-lesson-id",
  "modelVersion": "unconfigured",
  "inferenceStatus": "unavailable",
  "predictedClass": null,
  "confidence": null,
  "feedback": [{ "kind": "tracking", "text": "Posisikan tangan di dalam bingkai kamera." }],
  "assessment": { "handshape": null, "orientation": null, "movement": null, "face": null },
  "overallScore": null
}
```

### Realtime correctness rules

1. Landmark color indicates **tracking visibility/reliability** unless valid component scoring exists. It must not imply a specific finger is wrong without validated evaluator.
2. Use yellow + **“Belum yakin”**, text description and optional patterned marks; red/green accompanied by labels; never color-only.
3. Do not show percentages like `95% correct gesture` solely from a softmax score.
4. `No hand detected` is not a wrong ASL sign; stop score calculation.
5. Do not treat all valid signing variations as anomalies.
6. For face/pose, restrict scope to specific classes where nonmanual features matter and are validated.
7. Confidence threshold must be benchmarked/adjustable based on validation; no hardcoded random 0.80 advertised as scientific.
8. Measure model loading, latency, FPS, dropped frames, temperature/battery impact where feasible.

### Dataset, training, and evaluation

- Limit first supported classes to feasible subset; aim 20–30 **only if** trained, tested and reviewed.
- Include demographic/visual variation (handedness, lighting, backgrounds, signers) with consent and licensing.
- **Subject-independent split** train/validation/test: people in test must not appear in train.
- Establish baselines (e.g. landmark + classical classifier, simple MLP/GRU/LSTM) before BiLSTM conclusions.
- Metrics: precision, recall, macro-F1, confusion matrix, per-class support, unknown/reject behavior, latency (device), stability; report actual figures only.
- Track feature normalization, model version, dataset version, label map, consent, validation evidence.
- For scoring attributes, collect expert-annotated rubric rather than guessing each finger's correct angle from examples.

---

## 09. PWA, DATA, SECURITY AND PRIVACY

### PWA contract

- `manifest.webmanifest`: name SIGNTALK, short_name, icon 192/512 and maskable, theme/background, `display: standalone`, consistent scope/start URL.
- Vite PWA/Workbox: cache versioned shell, fonts, local artwork, known static lesson metadata, permitted owned video assets; never indiscriminately cache large AI models without storage budgeting.
- YouTube embed may not function offline; show clear offline messaging and locally available texts/images.
- Service worker update UX: non-blocking “Versi baru tersedia — Perbarui” with safe state preservation.
- Install-to-home-screen instructions for iOS Safari and Android; display any unsupported capabilities honestly.
- App shell usable offline for cached content and locally saved progress; AI inference offline **only if** its models/assets are cached and browser support verified; no blanket promises.
- Camera: HTTPS/localhost, explicit permission, device support/errors; allow practice without storing raw camera video by default.

### Data model / persistence

For early MVP: content catalog from versioned JSON or backend, preferences and consent via safe client persistence, progress via IndexedDB with versioned schema. For multi-device/synced research accounts: evaluate Supabase/Firebase/FastAPI backend after deciding authentication and privacy. Choose one authoritative backend path, not all simultaneously.

Entities (conceptual): `users`, `user_preferences`, `lessons`, `categories`, `video_sources`, `content_reviews`, `model_versions`, `supported_classes`, `practice_attempts`, `lesson_progress`, `consent_records`. `practice_attempts` stores time, class label, verdict, model version, supported component results, not raw frames unless separate explicit consent.

### Security/privacy

- Principle: camera frame processing *on-device by default*; if backend inference chosen, transparent notice, encryption, minimization, retention limits and consent before upload.
- Disable camera immediately on navigation away/unmount; stop MediaStream tracks; hide camera when backgrounded where feasible.
- Do not track biometric identifiers; landmark streams/face data may be sensitive.
- Permission to use camera ≠ consent for research data collection.
- Do not expose test datasets or users' captured frames via public URL, service worker, logs or analytics.
- Auth/RLS on backend if used; user can see/delete own attempts; admin cannot infer identities from public progress.

---

## 10. PERFORMANCE, DEVICE PROFILES AND 3D FALLBACK

### Profiles

- **Desktop strong:** full landing 3D scene, smooth camera path, real shadow quality, optional didactic hand explorer.
- **Tablet/mobile capable:** simplified meshes, light/material tuning, capped DPR, lower texture size, lower animation density, 3D scene as a short hero with content reachable promptly.
- **Low-power/reduced-motion/WebGL disabled:** complete editorial 2D equivalent, same lesson buttons, camera AI if available independent of Three.js.

### Engine requirements

- Lazy-load Three.js only for pages that need it. Do not ship it as critical bundle dependency for plain content pages.
- Use correct R3F version matching React version; prefer stable major, not alpha or unverified APIs.
- Validate WebGL feature + context initialization **and actual render**. Catch context lost and recover; fallback should be beautiful and not show debug text.
- Canvas has real CSS dimensions, camera bounds, lights, resize observer, and context cleanup; dispose geometries/materials/textures.
- Compress GLB (`glTF`/Draco/Meshopt where compatible); texture compression/WebP/AVIF; write licenses and source provenance.
- Avoid huge high-poly hand models, multiple WebGL contexts, excessive postprocessing on iPhone, per-frame React state.
- Set and measure performance budgets on target devices; never claim “60 FPS” without measurement.
- Camera scene and decorative 3D do not run simultaneously on low-power defaults; disable decor when practice is active.

### QA fault matrix

| Failure | Expected product response |
|---|---|
| WebGL unavailable | Strong 2D hero, all navigation works, no raw debug text |
| 3D model missing | Render useful fallback and log dev diagnostics, no invisible empty canvas |
| Camera denied | How to enable permission + link to video learning |
| No hands detected | “Posisikan tangan dalam bingkai,” no scoring |
| Model not loaded | “Latihan AI belum tersedia,” camera tracking can still be demoed if appropriate |
| AI uncertain | “Belum dapat memastikan isyarat,” retry guidance |
| YouTube blocked/offline | Context + alternative approved still frames/text, never auto-download copyrighted video |
| Offline no synced data | Local cache/progress, clear sync status |

---

## 11. MOTION DESIGN SPECIFICATION

| Type | Duration / trigger | Constraints |
|---|---|---|
| Hover/tap | 120–200 ms | No hover-only required actions |
| Page/route transition | 180–350 ms | Do not blank out content |
| Element reveal | 300–500 ms | One-time, text accessible immediately |
| 3D camera transition | Scroll-position dependent | Smooth, reversible, readable; max ~6 story beats |
| Hand explorer rotation | Direct touch/mouse/keyboard | No inertial surprise; reset button |
| Camera landmark overlay | Per valid processed frame | Aligned/low latency, no fake classification colors |
| Completion moment | 200–400 ms | Subtle and skippable |

- Refrain from sound-dependent instruction; visual captions mandatory. No autoplay voice needed.
- Avoid scroll hijack: native scrolling remains functional, keyboard PageDown/Space supported, focus remains stable.
- Text overlays are rendered in accessible HTML on top of 3D, *not* embedded as unreadable textures.
- All essential information is discoverable without animation or WebGL.

---

## 12. COMPONENTS / FOLDER STRUCTURE (PROPOSAL)

```text
signtalk/
├── public/
│   ├── models/                  # licensed 3D assets only
│   ├── media/                   # original/licensed visual materials
│   └── pwa/                     # manifest icons
├── src/
│   ├── app/                     # routes, layouts, error boundaries
│   ├── components/
│   │   ├── ui/                  # design system
│   │   ├── learning/            # lesson viewer and assessment
│   │   ├── vision/              # CameraPreview / LandmarkOverlay
│   │   └── three/               # ThreeStage / HandExplorer / Fallback
│   ├── features/
│   │   ├── content/
│   │   ├── practice/
│   │   ├── evaluation/
│   │   └── progress/
│   ├── ai/
│   │   ├── landmarks/           # MediaPipe adapter
│   │   ├── preprocessing/
│   │   ├── classifier/          # real model contract
│   │   └── assessment/          # expert-validated rubrics
│   ├── data/                    # versioned lesson metadata
│   ├── lib/                     # IndexedDB/PWA/permission helpers
│   ├── styles/                  # tokens/fonts/layout
│   └── tests/
├── models/                      # training/eval artifacts if appropriate; not raw personal video
├── docs/
│   ├── CONTENT_VALIDATION.md
│   ├── MODEL_CARD.md
│   ├── ASSET_LICENSES.md
│   └── TEST_REPORT.md
├── desain.md
├── PROMPT_OPENCODE.md
└── README.md
```

Do not force this structure if project already has a clean architecture.

---

## 13. IMPLEMENTATION PHASES & GATES

### P0 — Foundation, not a screenshot

- Create React/TS/Vite/PWA shell, routing, design tokens, responsive navigation, visible real lesson demo data with `reviewStatus` labels, IndexedDB/local progress.
- Implement educational flows without fake predictions. Lesson → video → practice preview → result states.
- Basic accessibility checks and link navigation.
- **Gate:** user can complete meaningful learning flow with camera permission still optional.

### P1 — Three.js hero proof-of-concept

- Load one working Canvas with visible geometry and first 2 meaningful scenes.
- Add real camera transform tied to scroll, responsive canvas sizing, DOM overlay CTA, 2D fallback.
- Verify in a real desktop browser, iPhone Safari if available, and mobile simulated viewport; record errors/limits.
- **Gate:** scroll really moves camera in scene, no clipped header, functional CTA/fallback. Do **not** declare 3D complete after only showing a static rotating object.

### P2 — Full motion journey + learning UI

- Finish 6-beat scroll journey; build vocabulary, phrases, detail page, search, video embeds, content-source attribution.
- Ensure layout is usable without 3D and on mobile. Add 3D Hand Explorer only with documented licensed asset / explicit illustration caveat.
- **Gate:** content navigation/accessibility works independently of scene renderer.

### P3 — Camera + MediaPipe

- Permission state machine, camera controls, hand landmark overlay, tracking feedback, frame throttling, device tests; optional face/pose only if specific content requires and benchmark permits.
- **Gate:** hand landmarks match video coordinates, mirror semantics correct, stop camera when leaving.

### P4 — Actual AI integration

- Audit real dataset; train/verify classifier on user-disjoint split; connect real model outputs, reject/unknown states and inference telemetry; document model card.
- Keep class gating: only classes trained/validated support AI button; unimplemented categories are learning-only.
- **Gate:** measurable held-out results, no mock prediction, no claim universal ASL recognition.

### P5 — Feedback, evaluation, persistence

- Add component-level feedback only for validated rubric/features; results with honest `not_assessed` fields, score only if designed and tested; progress history, optional auth/sync.
- **Gate:** every displayed grade maps to a concrete evaluator/method and real input.

### P6 — Research-grade polish

- User testing with consenting Tuli participants; ASL expert review; small/large screens, reduced motion, no WebGL, no camera, offline; test performance and privacy.
- **Gate:** acceptance report with **tested / untested / limitations**, not unfounded readiness claims.

---

## 14. TEST PLAN & ACCEPTANCE CRITERIA

### Visual

- Hero renders actual 3D geometry on supported desktop browsers; camera visibly changes along scroll milestones 0%, 25%, 50%, 75%, 100%.
- Every scene has coherent geometry/lighting/material, no clipped headline, no overlapping nav.
- Mobile layouts checked at 360, 390, 430, 768, 1024, 1440 px; usable with touch and keyboard.
- Fallback 2D is intentional and beautiful, not debug text.

### Functionality

- Vocabulary and phrases search/filter navigate to valid lessons.
- Videos load only if approved/embeddable; show empty/error states if blocked.
- Camera permission success/deny/not-found paths work; camera stops on exit.
- Hand overlay tracks actual hands; never displays fabricated model feedback.
- Only supported/validated classes show active AI evaluation; unsupported lessons still teach.
- Result page displays actual attempt data; progress persists after refresh; deletion works.
- PWA installability checks, offline states, update prompts, cache version handling.

### Model quality

- Each model artifact has label map, version, training/test method, inference benchmark, and known limitations.
- Validate on unseen signers, provide confusion matrix/macro-F1/per-class metrics; uncertainty behavior tested.
- If model absent, all scored UI shows unavailable state, not fake scores.
- Handshape or face-specific correction requires separate validation.

### User safety, inclusion and research

- Clear Indonesian guidance; no audio required; keyboard navigation, text alongside color cues.
- Review materials by competent ASL source; consult target Tuli participants and respect preferred terminology.
- Ask explicit research data consent independent of camera permission; default no raw video uploads.

---

## 15. BACKEND / DEPLOYMENT DECISION RECORD

**Recommended starting default:** Static React/Vite frontend, content JSON with review metadata, IndexedDB for personal progress, browser MediaPipe. No login required just to view lessons. Introduce Supabase or Firebase only when actually needed for accounts and synced progress, with documented RLS/security rules. Choose FastAPI **only** if real model inference is not feasible in browser or server evaluation is required; measure latency and operating cost first.

**Deployment:** hosting HTTPS with SPA fallback, service-worker scope correct, cache update tested, camera permissions tested on iPhone Safari. YouTube is online by nature; offline lesson text/images may remain available.

**Do not put video training data, secret API keys, service-role keys, or private consent logs in client bundle.**

---

## 16. SOURCE-OF-TRUTH CHECKLIST

| Topic | Current status from concept | Required before claims |
|---|---|---|
| Target learners | Defined as Tuli Indonesians interested in ASL | Need validation survey/interviews |
| ASL materials | Categories/phrases proposed | Competent ASL validation + sources/licenses |
| Vocabulary count | Target 20–30 classes | Actual selected supported list and dataset |
| Video references | YouTube official embeds proposed | Curated embeddable video IDs and permission terms |
| Hand tracking | MediaPipe intended | Tested live implementation |
| Face/pose | Desired for relevant signs | Device benchmark and linguistic relevance |
| BiLSTM | Candidate | Dataset baseline + training + unseen-signer evaluation |
| Realtime correction | Desired innovation | Validated component-level evaluation |
| Final scores | Example UI only | Formula/evidence/tests |
| Learning progress | Desired | Persistence + data lifecycle/privacy test |
| 3D hand demonstration | New art direction request | Valid licensed model + expert pose validation before ASL claims |

**End condition:** SIGNTALK must look impressive **and** be scientifically honest, accessible, and demonstrably functional. A rich homepage is not a substitute for a working learning/practice loop.
