import { FaceLandmarker, HandLandmarker, PoseLandmarker } from '@mediapipe/tasks-vision';
import { BookOpen, ExternalLink, LoaderCircle, RotateCcw, Shield, Upload, Volume2, VolumeX, X } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { EXPERIMENTAL_LABELS, EXPERIMENTAL_MODEL_VERSION, LocalOnnxRecognitionEngine, summarizeHandSequence, type RecognitionResult } from '../ai/recognition';
import SourceDemoMedia from '../SourceDemoMedia';
import { youtubeWatchUrl } from '../video';

const MODEL_BASE = `${import.meta.env.BASE_URL}mediapipe/`;
const WASM_BASE = `${import.meta.env.BASE_URL}mediapipe`;
const visionFiles = {
  wasmLoaderPath: `${WASM_BASE}/vision_wasm_nosimd_internal.js`,
  wasmBinaryPath: `${WASM_BASE}/vision_wasm_nosimd_internal.wasm`,
};
type Props = { stream: MediaStream; onStop: () => void; onSessionSaved: (attemptId: string) => void; targetGloss?: string; targetSteps?: readonly string[]; targetVideoUrl?: string; targetVideoTitle?: string; targetDemoUrl?: string; targetDemoType?: 'gif'|'mp4'; targetSource?: string };
type Point = { x: number; y: number };
type Connection = { start: number; end: number };

export default function HandTracking({ stream, onStop, onSessionSaved, targetGloss, targetSteps = [], targetVideoUrl, targetVideoTitle, targetDemoUrl, targetDemoType, targetSource }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const handRef = useRef<HandLandmarker | null>(null);
  const faceRef = useRef<FaceLandmarker | null>(null);
  const poseRef = useRef<PoseLandmarker | null>(null);
  const recognitionRef = useRef<LocalOnnxRecognitionEngine | null>(null);
  const frameBuffer = useRef<number[][][]>([]);
  const inferenceBusy = useRef(false);
  const lastPredictionAt = useRef(0);
  const reportedFrameCount = useRef(0);
  const reportedVisibleFrames = useRef(0);
  const [recognitionState, setRecognitionState] = useState<'unavailable'|'loading'|'ready'|'error'>('unavailable');
  const [recognitionMessage, setRecognitionMessage] = useState('Pilih model ONNX lokal untuk mengaktifkan prediksi eksperimen.');
  const [prediction, setPrediction] = useState<RecognitionResult | null>(null);
  const [modelLoadError, setModelLoadError] = useState('');
  const [frameProgress, setFrameProgress] = useState({ total: 0, visible: 0 });
  const [coachStepIndex, setCoachStepIndex] = useState(0);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [selfCheck, setSelfCheck] = useState<'matches_source'|'needs_guidance'|null>(null);
  const [state, setState] = useState('Memuat pelacak tangan…');
  const [error, setError] = useState('');
  const [handCount, setHandCount] = useState(0);
  const [guidance, setGuidance] = useState('Pastikan seluruh tangan terlihat di bingkai dan mendapat cahaya dari depan.');
  const [paused, setPaused] = useState(false);
  const [mirror, setMirror] = useState(true);
  const [faceEnabled, setFaceEnabled] = useState(false);
  const [poseEnabled, setPoseEnabled] = useState(false);
  const [faceStatus, setFaceStatus] = useState<'off'|'loading'|'ready'|'detected'|'error'>('off');
  const [poseStatus, setPoseStatus] = useState<'off'|'loading'|'ready'|'detected'|'error'>('off');
  const [retry, setRetry] = useState(0);
  const pausedRef = useRef(paused), mirrorRef = useRef(mirror);
  const faceEnabledRef = useRef(faceEnabled), poseEnabledRef = useRef(poseEnabled);
  pausedRef.current = paused; mirrorRef.current = mirror;
  faceEnabledRef.current = faceEnabled; poseEnabledRef.current = poseEnabled;
  const targetSupported = !!targetGloss && EXPERIMENTAL_LABELS.includes(targetGloss as typeof EXPERIMENTAL_LABELS[number]);
  const targetName = targetGloss?.toUpperCase() || 'isyarat ini';
  const coachMessage = error
    ? 'Aku belum bisa membaca frame. Coba muat ulang pelacak; kamu juga bisa lanjut belajar tanpa penilaian.'
    : recognitionState === 'loading'
      ? 'Aku sedang menyiapkan model lokal. Kamu bisa mulai menata tangan sambil menunggu.'
      : recognitionState === 'ready' && !targetSupported
        ? `Target ${targetName} belum termasuk enam kelas model. Aku tetap membantumu menjaga tangan terlihat dan memberi panduan dari materi, tetapi tidak akan menebak benar atau salah untuk isyarat ini.`
        : recognitionState === 'ready' && prediction?.predictedClass && prediction.status === 'recognized'
          ? prediction.predictedClass === targetGloss
            ? selfCheck==='matches_source'?`Kamu bilang gerakanmu sudah cocok dengan contoh ${targetName}. Bagus—model juga menebak target itu, tapi ini tetap bukan penilaian ahli.`:`Model menebak ${prediction.predictedClass.toUpperCase()}, sama dengan target ${targetName}. Cocokkan juga dengan demonstrasi sumber; tebakan model bukan bukti isyarat benar.`
            : selfCheck==='matches_source'?`Kamu sudah mengecek demonstrasi dan merasa gerakanmu cocok dengan ${targetName}. Aku catat itu. Model menebak ${prediction.predictedClass.toUpperCase()}, tetapi tebakan model bisa salah—jangan jadikan itu vonis.`:selfCheck==='needs_guidance'?`Kita cek lagi target ${targetName} dari sumber. Model menebak ${prediction.predictedClass.toUpperCase()}, tetapi itu belum membuktikan gerakanmu salah.`:`Target latihan ${targetName}; model menebak ${prediction.predictedClass.toUpperCase()}. Ini hanya tebakan dan bisa keliru. Bandingkan bentuk serta arah gerak dengan demonstrasi sebelum mengubah gerakanmu.`
          : recognitionState === 'ready' && prediction
            ? 'Aku belum cukup yakin dengan prediksi ini. Pastikan seluruh tangan terlihat, tahan gerakan sebentar, lalu ulangi.'
            : recognitionState === 'ready' && frameProgress.total >= 32 && frameProgress.visible < 16
              ? `Aku baru melihat tangan pada ${frameProgress.visible} dari 32 frame. Tahan tangan utuh di tengah kamera sampai terlihat setidaknya 16 frame.`
              : recognitionState === 'ready'
                ? `Aku sedang mengamati 32 frame. Saat ini ${frameProgress.visible} frame menunjukkan tangan; lakukan gerakan target ${targetName} dengan jelas.`
                : handCount === 0
                  ? 'Aku belum melihat tanganmu. Angkat tangan ke tengah kamera, pastikan ujung jari terlihat, lalu mulai gerakkan perlahan.'
                  : guidance;

  useEffect(() => {
    if (!voiceEnabled || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const currentStep = targetSteps[coachStepIndex];
    const utterance = new SpeechSynthesisUtterance(currentStep ? `${coachMessage} Langkah latihan. ${currentStep}` : coachMessage);
    utterance.lang = 'id-ID'; utterance.rate = .96;
    window.speechSynthesis.speak(utterance);
    return () => window.speechSynthesis.cancel();
  }, [coachMessage, coachStepIndex, targetSteps, voiceEnabled]);

  useEffect(() => () => { recognitionRef.current?.dispose(); recognitionRef.current = null; }, []);

  async function loadModel(file?: File) {
    if (!file) return;
    recognitionRef.current?.dispose(); recognitionRef.current = null;
    setPrediction(null); setModelLoadError(''); setRecognitionState('loading');
    setRecognitionMessage('Memuat model di perangkat ini…');
    try {
      const engine = new LocalOnnxRecognitionEngine();
      await engine.load(file, EXPERIMENTAL_LABELS);
      recognitionRef.current = engine;
      frameBuffer.current = [];
      reportedFrameCount.current = 0;
      reportedVisibleFrames.current = 0;
      setFrameProgress({ total: 0, visible: 0 });
      setRecognitionState('ready');
      setRecognitionMessage(`${EXPERIMENTAL_MODEL_VERSION}. Prediksi bukan penilaian benar/salah.`);
    } catch (cause) {
      setRecognitionState('error');
      setModelLoadError(cause instanceof Error ? cause.message : 'Model tidak dapat dimuat.');
      setRecognitionMessage('Model tidak aktif. Kamera dan tracking tetap dapat digunakan.');
    }
  }

  useEffect(() => {
    let active = true;
    let raf = 0;
    let lastInference = 0;
    const loadTimeout = window.setTimeout(() => setError('Pelacak tangan belum selesai dimuat. Periksa dukungan browser/perangkat, lalu muat ulang.'), 30000);
    const video = videoRef.current!;
    video.srcObject = stream;
    void video.play().catch(() => setError('Preview kamera belum dapat diputar. Pastikan izin kamera aktif lalu muat ulang pelacak.'));
    handRef.current?.close(); handRef.current = null;

    const setup = async () => {
      try {
        setState('Memuat runtime hand tracking…');
        const handOptions = { runningMode: 'VIDEO' as const, numHands: 2, minHandDetectionConfidence: .35, minHandPresenceConfidence: .35, minTrackingConfidence: .35 };
        handRef.current = await HandLandmarker.createFromOptions(visionFiles, {
          ...handOptions, baseOptions: { modelAssetPath: `${MODEL_BASE}hand_landmarker.task`, delegate: 'CPU' },
        });
        if (!active) { handRef.current?.close(); handRef.current = null; return; }
        window.clearTimeout(loadTimeout); setError(''); setState('Tangan belum terlihat');

        const loop = (now: number) => {
          if (!active) return;
          raf = requestAnimationFrame(loop);
          const interval = faceEnabledRef.current || poseEnabledRef.current ? 160 : 80;
          if (pausedRef.current || document.hidden || video.readyState < 2 || now - lastInference < interval) return;
          lastInference = now;
          try {
            const hands = handRef.current?.detectForVideo(video, now).landmarks ?? [];
            const orderedForModel = [...hands].sort((a, b) => a.reduce((sum, point) => sum + point.x, 0) - b.reduce((sum, point) => sum + point.x, 0)).slice(0, 2);
            const modelFrame = [0, 1].map(slot => orderedForModel[slot]?.flatMap(point => [point.x, point.y, point.z]) ?? []);
            frameBuffer.current.push(modelFrame);
            if (frameBuffer.current.length > 32) frameBuffer.current.shift();
            const visibleFrames = frameBuffer.current.filter(frame => frame.some(hand => hand.length === 63)).length;
            if (recognitionRef.current && targetSupported && (frameBuffer.current.length !== reportedFrameCount.current || visibleFrames !== reportedVisibleFrames.current)) {
              reportedFrameCount.current = frameBuffer.current.length;
              reportedVisibleFrames.current = visibleFrames;
              setFrameProgress({ total: frameBuffer.current.length, visible: visibleFrames });
            }
            if (recognitionRef.current && targetSupported && frameBuffer.current.length === 32 && visibleFrames >= 16 && now - lastPredictionAt.current > 900 && !inferenceBusy.current) {
              inferenceBusy.current = true;
              lastPredictionAt.current = now;
              void recognitionRef.current.recognize(summarizeHandSequence(frameBuffer.current)).then(setPrediction).catch(() => {
                setModelLoadError('Inferensi gagal. Muat ulang model atau lanjutkan tracking tanpa prediksi.');
                setRecognitionState('error'); recognitionRef.current?.dispose(); recognitionRef.current = null;
              }).finally(() => { inferenceBusy.current = false; });
            }
            const faces = faceRef.current?.detectForVideo(video, now).faceLandmarks ?? [];
            const poses = poseRef.current?.detectForVideo(video, now).landmarks ?? [];
            if (faceRef.current) setFaceStatus(faces.length ? 'detected' : 'ready');
            if (poseRef.current) setPoseStatus(poses.length ? 'detected' : 'ready');
            setHandCount(hands.length);
            setState(hands.length ? `${hands.length} tangan terlacak` : 'Tangan belum terlihat');
            if (!hands.length) setGuidance('Tangan belum terlihat. Hadapkan telapak ke kamera dan pastikan ujung jari masuk seluruhnya.');
            else {
              const points = hands.flat();
              const minX = Math.min(...points.map(point => point.x)), maxX = Math.max(...points.map(point => point.x));
              const minY = Math.min(...points.map(point => point.y)), maxY = Math.max(...points.map(point => point.y));
              const centerX = (minX + maxX) / 2, centerY = (minY + maxY) / 2;
              setGuidance(minX < .04 || maxX > .96 || minY < .04 || maxY > .96
                ? 'Sebagian tangan terlalu dekat tepi. Mundurkan atau geser agar seluruh tangan masuk frame.'
                : (centerX < .32 || centerX > .68 || centerY < .25 || centerY > .78)
                  ? 'Tangan terdeteksi. Pindahkan sedikit mendekati tengah frame.'
                  : maxX - minX < .16 || maxY - minY < .2
                    ? 'Tangan terdeteksi. Dekatkan sedikit ke kamera agar landmark lebih jelas.'
                    : 'Tangan berada di dalam frame. Landmark hanya menunjukkan tracking, bukan ketepatan ASL.');
            }

            const canvas = canvasRef.current, ctx = canvas?.getContext('2d');
            if (!canvas || !ctx || !video.videoWidth) return;
            const bounds = canvas.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 2);
            if (canvas.width !== Math.round(bounds.width * dpr) || canvas.height !== Math.round(bounds.height * dpr)) {
              canvas.width = Math.round(bounds.width * dpr); canvas.height = Math.round(bounds.height * dpr);
            }
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const scale = Math.min(canvas.width / video.videoWidth, canvas.height / video.videoHeight);
            const ox = (canvas.width - video.videoWidth * scale) / 2, oy = (canvas.height - video.videoHeight * scale) / 2;
            const xy = (point: Point): [number, number] => [ox + point.x * video.videoWidth * scale, oy + point.y * video.videoHeight * scale];
            const drawConnections = (points: Point[], connections: Connection[], color: string, width: number) => {
              ctx.strokeStyle = color; ctx.lineWidth = width * dpr;
              for (const { start, end } of connections) {
                if (!points[start] || !points[end]) continue;
                const a = xy(points[start]), b = xy(points[end]);
                ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
              }
            };
            ctx.save();
            if (mirrorRef.current) { ctx.translate(canvas.width, 0); ctx.scale(-1, 1); }
            // Distinct overlay colors encode detector types only; none denotes ASL correctness.
            for (const hand of hands) {
              drawConnections(hand, HandLandmarker.HAND_CONNECTIONS, '#b9f1dd', 2);
              ctx.fillStyle = '#153b46'; ctx.strokeStyle = '#dff9ee'; ctx.lineWidth = 1.2 * dpr;
              for (const point of hand) { const [x,y] = xy(point); ctx.beginPath(); ctx.arc(x,y,3.2*dpr,0,Math.PI*2); ctx.fill(); ctx.stroke(); }
            }
            if (faceRef.current && faces[0]) drawConnections(faces[0], FaceLandmarker.FACE_LANDMARKS_FACE_OVAL, '#eabf75', 1.5);
            if (poseRef.current && poses[0]) drawConnections(poses[0], PoseLandmarker.POSE_CONNECTIONS, '#9bc6f5', 2);
            ctx.restore();
          } catch {
            setError('Frame kamera belum dapat diproses. Jeda kamera atau muat ulang pelacak.');
          }
        };
        raf = requestAnimationFrame(loop);
      } catch (cause) {
        window.clearTimeout(loadTimeout);
        setError(cause instanceof Error ? `Pelacak tangan tidak dapat dimuat: ${cause.message}` : 'Pelacak tangan tidak dapat dimuat.');
      }
    };
    const visibility = () => { stream.getVideoTracks().forEach(track => { track.enabled = !document.hidden; }); if (document.hidden) video.pause(); else void video.play().catch(() => {}); };
    document.addEventListener('visibilitychange', visibility);
    void setup();
    return () => {
      active = false; window.clearTimeout(loadTimeout); document.removeEventListener('visibilitychange', visibility); cancelAnimationFrame(raf);
      handRef.current?.close(); handRef.current = null;
    };
  }, [stream, retry, targetSupported]);

  useEffect(() => {
    let active = true;
    faceRef.current?.close(); faceRef.current = null;
    if (!faceEnabled) { setFaceStatus('off'); return () => { active = false; }; }
    setFaceStatus('loading');
    void FaceLandmarker.createFromOptions(visionFiles, {
      baseOptions: { modelAssetPath: `${MODEL_BASE}face_landmarker.task`, delegate: 'CPU' },
      runningMode: 'VIDEO', numFaces: 1, outputFaceBlendshapes: false, outputFacialTransformationMatrixes: false,
    }).then(detector => {
      if (!active) { detector.close(); return; }
      faceRef.current = detector; setFaceStatus('ready');
    }).catch(() => { if (active) setFaceStatus('error'); });
    return () => { active = false; faceRef.current?.close(); faceRef.current = null; };
  }, [stream, retry, faceEnabled]);

  useEffect(() => {
    let active = true;
    poseRef.current?.close(); poseRef.current = null;
    if (!poseEnabled) { setPoseStatus('off'); return () => { active = false; }; }
    setPoseStatus('loading');
    void PoseLandmarker.createFromOptions(visionFiles, {
      baseOptions: { modelAssetPath: `${MODEL_BASE}pose_landmarker_lite.task`, delegate: 'CPU' },
      runningMode: 'VIDEO', numPoses: 1, outputSegmentationMasks: false,
    }).then(detector => {
      if (!active) { detector.close(); return; }
      poseRef.current = detector; setPoseStatus('ready');
    }).catch(() => { if (active) setPoseStatus('error'); });
    return () => { active = false; poseRef.current?.close(); poseRef.current = null; };
  }, [stream, retry, poseEnabled]);

  function finish() {
    stream.getTracks().forEach(track => track.stop());
    const id = crypto.randomUUID();
    const attempts = JSON.parse(localStorage.getItem('signtalk-attempts') || '[]') as Array<{id:string;lessonId:string;date:string;outcome:string;handsDetected:number;modelPrediction?:string|null;targetGloss?:string|null;modelConfidence?:number|null;referenceCheck?:'matches_source'|'needs_guidance'|null}>;
    const supportedTarget=targetGloss&&EXPERIMENTAL_LABELS.includes(targetGloss as typeof EXPERIMENTAL_LABELS[number])?targetGloss:null;
    attempts.unshift({ id, lessonId: location.pathname.split('/').pop() || '', date: new Date().toISOString(), outcome: 'not_assessed', handsDetected: handCount, modelPrediction:prediction?.predictedClass??null, targetGloss:supportedTarget, modelConfidence:prediction?.confidence??null, referenceCheck:selfCheck });
    localStorage.setItem('signtalk-attempts', JSON.stringify(attempts));
    onSessionSaved(id);
  }
  function retrySign() {
    frameBuffer.current = []; reportedFrameCount.current = 0; reportedVisibleFrames.current = 0; inferenceBusy.current = false; lastPredictionAt.current = 0;
    setFrameProgress({ total: 0, visible: 0 }); setPrediction(null); setSelfCheck(null); setModelLoadError('');
  }
  return <div className="live-practice-grid">
    <section className="live-camera-column" aria-label="Pratinjau kamera dan tracking">
      <div className="live-camera-heading"><div><span className="section-kicker">KAMERA LANGSUNG</span><h2>{targetName}</h2></div><span className="live-track-pill">{error||state}</span></div>
      <div className="camera-box tracking-box"><video ref={videoRef} autoPlay muted playsInline className={mirror ? 'mirrored' : ''}/><canvas ref={canvasRef}/><span className="tracking-status" aria-live="polite">{error || state}</span></div>
      <p className="vision-status" aria-live="polite">Wajah: {faceStatus==='off'?'nonaktif':faceStatus==='loading'?'memuat':faceStatus==='error'?'gagal dimuat':faceStatus==='detected'?'terdeteksi':'mencari'} · Tubuh/pose: {poseStatus==='off'?'nonaktif':poseStatus==='loading'?'memuat':poseStatus==='error'?'gagal dimuat':poseStatus==='detected'?'terdeteksi':'mencari'}. Tidak ada penilaian ekspresi atau postur.</p>
      <p className="tracking-note" aria-live="polite">{error ? 'Landmark belum tersedia; preview tetap lokal. Periksa kompatibilitas browser dan coba muat ulang pelacak.' : guidance}</p>
      <div className="vision-options"><label><input type="checkbox" checked={faceEnabled} onChange={event=>setFaceEnabled(event.target.checked)}/> Lacak landmark wajah (deteksi saja)</label><label><input type="checkbox" checked={poseEnabled} onChange={event=>setPoseEnabled(event.target.checked)}/> Lacak landmark tubuh (deteksi saja)</label></div>
      <div className="notice"><Shield/> Landmark tangan/wajah/pose adalah deteksi posisi saja; bukan pengenalan atau evaluasi bahasa isyarat.</div>
      <div className="practice-controls">{error&&<button className="button secondary" onClick={()=>{setError('');setRetry(x=>x+1)}}>Muat ulang pelacak</button>}<button className="button secondary" onClick={() => setMirror(x => !x)}>{mirror ? 'Matikan cermin' : 'Cerminkan preview'}</button><button className="button secondary" onClick={() => setPaused(x => !x)}>{paused ? 'Lanjutkan' : 'Jeda tracking'}</button><button className="button primary" onClick={finish}>Selesaikan sesi</button><button className="button secondary" onClick={onStop}>Matikan kamera</button></div>
    </section>
    <aside className="live-feedback-column" aria-label="Prediksi dan arahan coach">
    <section className="recognition-panel" aria-labelledby="recognition-heading">
      <div className="recognition-heading"><div><span className="eyebrow">LAB MODEL LOKAL · OPSIONAL</span><h2 id="recognition-heading">Prediksi isyarat tunggal</h2></div><span className={`model-pill model-${recognitionState}`}>{recognitionState==='ready'?'Model aktif':recognitionState==='loading'?'Memuat model':recognitionState==='error'?'Model bermasalah':'Tracking saja'}</span></div>
      <p className="recognition-copy">Model riset ini hanya mengenali enam gloss terisolasi: before, go, help, no, who, yes. Pilih file lokal <code>models/asl_citizen_6class_hand_logreg.onnx</code>. File tidak diunggah. Pertama kali dipakai, runtime inferensi mengunduh sekitar 30 MB. Kecocokan target adalah prediksi model, bukan bukti isyarat benar.</p>
      <label className="model-upload"><Upload size={17}/><span>{recognitionState==='loading'?'Memuat model…':'Pilih file model ONNX'}</span><input type="file" accept=".onnx,application/onnx" disabled={recognitionState==='loading'} onChange={event=>{void loadModel(event.target.files?.[0]);event.currentTarget.value='';}}/></label>
      {modelLoadError&&<p className="model-error" role="alert"><X size={16}/>{modelLoadError}</p>}
      {recognitionState==='loading'&&<p className="model-message"><LoaderCircle className="spin" size={16}/>{recognitionMessage}</p>}
      {recognitionState==='ready'&&targetSupported&&<div className="capture-progress"><div className="capture-progress-label"><span>Jendela sampel langsung</span><b>{Math.min(frameProgress.visible,16)}/16 frame tangan terlihat</b></div><progress max={16} value={Math.min(frameProgress.visible,16)} aria-label="Frame tangan yang dapat dianalisis"/><small>Model melihat 32 frame terakhir dan membutuhkan tangan terlihat pada minimal 16 frame.</small></div>}
      {recognitionState==='ready'&&!targetSupported&&<p className="model-limit"><Shield size={16}/> Target <b>{targetName}</b> tidak termasuk kelas model. Model sengaja tidak dipakai untuk menebak isyarat ini.</p>}
      {recognitionState==='ready'&&targetSupported&&<div className="prediction-box" aria-live="polite">{prediction?.predictedClass?<><span className="prediction-label">Tebakan model (bukan nilai)</span><strong>{prediction.predictedClass}</strong><b className={`target-comparison ${prediction.status==='recognized'&&prediction.predictedClass===targetGloss?'target-match':''}`}>{prediction.status!=='recognized'?'Model belum cukup yakin untuk dibandingkan.':prediction.predictedClass===targetGloss?`Model menebak target ${targetName}. Cocokkan juga dengan video sumber.`:`Target latihan ${targetName}; model menebak ${prediction.predictedClass.toUpperCase()}. Model bisa keliru—ini bukan vonis kamu salah.`}</b></>:<span>{recognitionMessage} Mengumpulkan sampel gerakan…</span>}</div>}
      {recognitionState==='ready'&&<p className="model-labels">Kelas: {EXPERIMENTAL_LABELS.join(' · ')}</p>}
    </section>
    <section className="coach-response" aria-live="polite" aria-atomic="true">
      <div className="coach-response-top"><div className="coach-avatar" aria-hidden="true">S</div><div><span className="section-kicker">COACH SIGNTALK · RESPONS LANGSUNG</span><h2>{prediction?.predictedClass&&prediction.status==='recognized'&&targetSupported?(prediction.predictedClass===targetGloss?'Model menebak target':selfCheck==='matches_source'?'Kamu sudah memeriksa sumber':'Model belum sepakat'):handCount?'Aku melihat tanganmu':'Aku siap membantumu'}</h2></div></div>
      <div className="coach-response-body"><div><p className="coach-message">{coachMessage}</p>{targetSteps.length>0&&<div className="coach-cue"><span>LANGKAH {coachStepIndex+1} / {targetSteps.length}</span><p>{targetSteps[coachStepIndex]}</p></div>}</div>{targetDemoUrl&&targetDemoType?<div className="coach-demo-video"><SourceDemoMedia src={targetDemoUrl} title={`${targetGloss||'Target'} — demonstrasi ASL University`} mediaType={targetDemoType}/><small>Media signer dari ASL University {targetSource&&<>· <a href={targetSource} target="_blank" rel="noreferrer">Buka sumber</a></>}</small></div>:targetVideoUrl?<div className="coach-demo-fallback"><BookOpen size={25}/><b>Video pengajar tersedia di YouTube</b><span>Player dibuka terpisah agar kontrolnya tidak menutupi contoh saat kamu mengamati kamera.</span><a href={youtubeWatchUrl(targetVideoUrl)} target="_blank" rel="noreferrer">Tonton video sumber <ExternalLink size={14}/></a>{targetSource&&<a href={targetSource} target="_blank" rel="noreferrer">Buka halaman materi <ExternalLink size={14}/></a>}</div>:<div className="coach-demo-fallback"><BookOpen size={25}/><b>Video demonstrasi belum tersedia untuk target ini.</b>{targetSource&&<a href={targetSource} target="_blank" rel="noreferrer">Buka halaman sumber <ExternalLink size={14}/></a>}</div>}</div>
      <div className="coach-actions"><button className="button secondary" type="button" onClick={()=>setVoiceEnabled(value=>!value)} aria-pressed={voiceEnabled}>{voiceEnabled?<VolumeX size={16}/>:<Volume2 size={16}/>} {voiceEnabled?'Matikan suara coach':'Dengarkan coach'}</button>{targetSteps.length>1&&<button className="button secondary" type="button" onClick={()=>setCoachStepIndex(index=>(index+1)%targetSteps.length)}>Langkah berikutnya</button>}{targetSupported&&prediction&&<><button className="button secondary" type="button" aria-pressed={selfCheck==='matches_source'} onClick={()=>setSelfCheck('matches_source')}>Sudah cocok dengan contoh</button><button className="button secondary" type="button" aria-pressed={selfCheck==='needs_guidance'} onClick={()=>{setSelfCheck('needs_guidance');setCoachStepIndex(index=>(index+1)%Math.max(targetSteps.length,1));}}>Aku perlu panduan lagi</button></>}{targetSupported&&recognitionState==='ready'&&<button className="button secondary" type="button" onClick={retrySign}><RotateCcw size={16}/> Ulangi analisis</button>}</div>
      <small className="coach-boundary">Aku bisa membimbing framing dan melaporkan prediksi eksperimen. Aku tidak akan menyebut isyaratmu benar atau salah tanpa evaluator yang tervalidasi.</small>
    </section>
    </aside>
  </div>;
}
