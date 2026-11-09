import type * as OrtTypes from 'onnxruntime-web';

/** Local experimental model interface; model files are never bundled or uploaded. */
export type RecognitionStatus = 'recognized' | 'uncertain' | 'incomplete' | 'not_supported' | 'model_unavailable';
export type RecognitionResult = {
  status: RecognitionStatus;
  predictedClass: string | null;
  modelVersion: string | null;
  confidence: number | null;
};

export const EXPERIMENTAL_MODEL_VERSION = 'ASL Citizen 6-class Logistic Regression v2 · eksperimen';
export const EXPERIMENTAL_LABELS = ['before', 'go', 'help', 'no', 'who', 'yes'] as const;

/** Mirrors ai/features.py temporal_summary() exactly for two screen-x-ordered hands. */
export function summarizeHandSequence(sequence: readonly (readonly (readonly number[])[])[]): Float32Array {
  if (sequence.length !== 32) throw new Error('Exactly 32 sampled frames are required.');
  const result: number[] = [];
  for (let slot = 0; slot < 2; slot++) {
    const pointsByFrame = sequence.map(frame => frame[slot]);
    const valid = pointsByFrame.filter(points => points?.length === 63);
    result.push(valid.length / sequence.length);
    if (!valid.length) { result.push(...new Array(21 * 3 * 7).fill(0)); continue; }
    const summaries = Array.from({ length: 7 }, () => Array.from({ length: 21 }, () => [0, 0, 0]));
    for (let point = 0; point < 21; point++) for (let axis = 0; axis < 3; axis++) {
      const values = valid.map(row => row[point * 3 + axis]);
      const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
      const deltas = values.slice(1).map((value, index) => Math.abs(value - values[index]));
      summaries[0][point][axis] = mean;
      summaries[1][point][axis] = Math.sqrt(values.reduce((sum, value) => sum + (value - mean) ** 2, 0) / values.length);
      summaries[2][point][axis] = values[0];
      summaries[3][point][axis] = values[values.length - 1];
      summaries[4][point][axis] = Math.min(...values);
      summaries[5][point][axis] = Math.max(...values);
      summaries[6][point][axis] = deltas.length ? deltas.reduce((sum, value) => sum + value, 0) / deltas.length : 0;
    }
    // Python stacks (7,21,3), transposes to (21,3,7), then flattens.
    for (let point = 0; point < 21; point++) for (let axis = 0; axis < 3; axis++)
      for (let summary = 0; summary < 7; summary++) result.push(summaries[summary][point][axis]);
  }
  return Float32Array.from(result);
}

export class LocalOnnxRecognitionEngine {
  private session: OrtTypes.InferenceSession | null = null;
  private labels: string[] = [];
  get status(): 'ready' | 'model_unavailable' { return this.session ? 'ready' : 'model_unavailable'; }
  get supportedLabels(): readonly string[] { return this.labels; }

  async load(file: File, labels: readonly string[] = EXPERIMENTAL_LABELS): Promise<void> {
    this.dispose();
    if (!file.name.toLowerCase().endsWith('.onnx')) throw new Error('Pilih file model .onnx.');
    const ort = await import('onnxruntime-web');
    const session = await ort.InferenceSession.create(await file.arrayBuffer(), { executionProviders: ['wasm'] });
    if (session.inputNames.length !== 1 || session.inputNames[0] !== 'features' || !session.outputNames.includes('probabilities')) {
      await session.release(); throw new Error('Format model tidak cocok dengan skema SIGNTALK.');
    }
    // Label order is exported in the companion metadata JSON, supplied separately by caller.
    const probabilities = session.outputNames.includes('probabilities');
    if (!probabilities || labels.length !== 6) {
      await session.release(); throw new Error('Output probabilitas/label model tidak cocok.');
    }
    this.labels = [...labels];
    this.session = session;
  }

  async recognize(features: Float32Array): Promise<RecognitionResult> {
    if (!this.session) return { status: 'model_unavailable', predictedClass: null, modelVersion: null, confidence: null };
    if (features.length !== 884 || this.labels.length !== 6) return { status: 'incomplete', predictedClass: null, modelVersion: EXPERIMENTAL_MODEL_VERSION, confidence: null };
    const ort = await import('onnxruntime-web');
    const output = await this.session.run({ features: new ort.Tensor('float32', features, [1, 884]) });
    const probabilities = output.probabilities?.data as Float32Array | undefined;
    if (!probabilities?.length) return { status: 'incomplete', predictedClass: null, modelVersion: EXPERIMENTAL_MODEL_VERSION, confidence: null };
    let best = 0;
    for (let i = 1; i < probabilities.length; i++) if (probabilities[i] > probabilities[best]) best = i;
    const confidence = probabilities[best];
    return { status: confidence >= 0.65 ? 'recognized' : 'uncertain', predictedClass: this.labels[best] ?? null, modelVersion: EXPERIMENTAL_MODEL_VERSION, confidence };
  }

  dispose(): void { void this.session?.release(); this.session = null; this.labels = []; }
}

/** App-level truthful default until a user explicitly loads a local model file. */
export const signRecognitionEngine = {
  get status(): 'ready' | 'model_unavailable' { return 'model_unavailable'; },
  supportedLabels: [] as readonly string[],
  async load() { return false; },
  async recognize(): Promise<RecognitionResult> {
    return { status: 'model_unavailable', predictedClass: null, modelVersion: null, confidence: null };
  },
  dispose() {},
};
