import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { VitePWA } from 'vite-plugin-pwa';
export default defineConfig({
  plugins:[react(),tailwindcss(),VitePWA({registerType:'autoUpdate',includeAssets:['pwa-icon.svg','pwa/icon-180.png','pwa/icon-192.png','pwa/icon-512.png'],workbox:{globIgnores:['**/mediapipe/**','**/ort-wasm-*.wasm'],runtimeCaching:[{urlPattern:/ort-wasm-.*\.wasm$/,handler:'CacheFirst',options:{cacheName:'onnx-wasm-runtime',expiration:{maxEntries:2,maxAgeSeconds:31536000}}}]},manifest:{name:'SIGNTALK',short_name:'SIGNTALK',description:'Pembelajaran ASL yang jujur dan aksesibel',theme_color:'#153b4b',background_color:'#f7f8f6',display:'standalone',start_url:'/',icons:[{src:'/pwa/icon-192.png',sizes:'192x192',type:'image/png',purpose:'any'},{src:'/pwa/icon-512.png',sizes:'512x512',type:'image/png',purpose:'maskable'},{src:'/pwa-icon.svg',sizes:'any',type:'image/svg+xml',purpose:'any'}]}})],
  build:{rolldownOptions:{output:{codeSplitting:{groups:[{name:'three-core',test:/node_modules[\\/]three[\\/]/,priority:20,maxSize:450_000},{name:'react-three',test:/node_modules[\\/]@react-three[\\/]/,priority:10,maxSize:450_000}]}}}},
  server:{host:'0.0.0.0'}
});
