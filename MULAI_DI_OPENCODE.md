# Cara menjalankan paket SIGNTALK dengan OpenCode

## Siapkan folder

1. Buat folder proyek `SIGNTALK` di laptop; jangan masukkan dalam folder website Beneranjualan.id.
2. Salin `desain.md` dan `PROMPT_OPENCODE.md` ke root folder SIGNTALK.
3. Jika tersedia, salin juga `KONSEP AWAL SIGNTALK.pdf` dan teks konsep lanjutan sebagai bahan rujukan ke `docs/references/`.
4. Buka PowerShell di root SIGNTALK, lalu jalankan `opencode`.
5. Beri instruksi singkat: **"Baca `desain.md` dan `PROMPT_OPENCODE.md` sampai selesai. Implementasikan tahapan P0/P1 terlebih dahulu secara nyata, inspeksi hasil render dan lanjutkan fase berikutnya dengan jujur terhadap ketersediaan dataset dan model."**

## Cara uji dasar setelah agent membuat proyek

```powershell
npm install
npm run dev
```

Buka URL yang ditampilkan Vite, biasanya `http://localhost:5173`. Kamera di browser laptop dapat diakses lewat localhost; untuk iPhone gunakan **HTTPS** pada deployment/pengujian (bukan membuka IP LAN lewat HTTP untuk kamera).

## Penting

- Three.js adalah bagian pengalaman visual; **tidak otomatis mengenali ASL**.
- MediaPipe mendeteksi landmark; klasifikasi ASL memerlukan model terlatih.
- Hasil Mini Challenge nyata baru bisa diberikan untuk kelas yang didukung model dan evaluator.
- Materi dan demonstrasi ASL perlu persetujuan ahli; tautan video YouTube harus dapat di-embed secara sah.
- Proyek PWA dapat dibuka dari iPhone Safari; memasang ke Home Screen perlu manifest, HTTPS dan instalasi yang diuji.

## Referensi dokumentasi teknologi

- React Three Fiber: https://r3f.docs.pmnd.rs/
- MediaPipe Hand Landmarker Web: https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/web_js
- Vite PWA plugin: https://vite-pwa-org.netlify.app/
- Browser camera: https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
- YouTube IFrame API: https://developers.google.com/youtube/iframe_api_reference
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
