# SIGNTALK

Prototipe PWA pembelajaran ASL berbahasa Indonesia. Materi rujukan berstatus `in_review`; aplikasi belum menyediakan klasifikasi atau penilaian ketepatan ASL.

## Menjalankan

```bash
npm install
npm run dev
```

Buka URL yang tercetak di terminal Vite. Untuk menguji PWA hasil build:

```bash
npm run build
npm run preview
```

Test installation on Android/desktop from Chrome/Edge's install action or on iOS Safari via **Share → Add to Home Screen**. Camera access requires HTTPS or localhost.

Kamera memerlukan `localhost` atau HTTPS dan baru diminta setelah tombol **Aktifkan kamera** ditekan. MediaPipe WASM dan model hand-landmarker resmi disertakan lokal untuk menghindari kegagalan CDN saat membuka kamera. Aset kamera tidak dimasukkan ke cache offline PWA secara otomatis karena ukurannya besar. Landmark adalah hasil deteksi tangan, bukan pengenalan atau penilaian isyarat.

## QA otomatis

- `npm run test:browser` — Chrome smoke test, screenshot scroll 3D, rute belajar, ukuran layar, keadaan kamera ditolak, MediaPipe dengan kamera virtual, penyimpanan sesi, dan fallback WebGL. Set `SIGNTALK_BASE_URL` bila Vite berjalan di port berbeda dan `CHROME_EXECUTABLE_PATH` bila Chrome tidak berada di lokasi Windows standar.
- `npm run test:pwa` — service worker dan navigasi katalog offline pada server preview. Jalankan sesudah `npm run build` dan `npm run preview`.
- `npm run generate:icons` — regenerate original Apple 180 and PWA 192/512 PNG icons from `public/pwa-icon.svg`.

Lihat `IMPLEMENTATION_PROGRESS.md`, `docs/STATUS.md`, `docs/FEATURE_STATUS.md`, dan `docs/DATASET_GUIDE.md` untuk hasil QA, status fitur, lisensi/batasan data, dan langkah pipeline.
