import tokens from "../../config/brand_tokens.json";

export const C = tokens.colors;
export const MONO = `'${tokens.fonts.mono}', Consolas, monospace`;
export const SANS = `'${tokens.fonts.sans}', 'Inter Variable', 'Segoe UI', sans-serif`;
export const VIDEO = tokens.video;

export type Scene = {
  id: string;
  type: "diagram" | "terminal" | "code";
  asset?: string;
  output?: string; // filled in by pipeline/generator.py
  duration_s: number;
  narration: string;
  aspect?: number; // image w/h, filled in by the generator
  highlight_lines?: number[]; // code scenes: rendered into the card
  camera?: {
    initial_zoom?: number; // start scale, centered
    pan_to?: string; // subgraph/node id in the diagram
    focus?: [number, number, number, number]; // its box [x, y, w, h] in %, filled in by the generator
  };
};

export type Manifest = {
  epId: string;
  title: string;
  scenes: Scene[];
};

// 16:9 safe zones. Captions sit SAFE_BOTTOM px above the edge; visuals stay above CAPTION_BAND (room for 3 caption lines).
export const SAFE_BOTTOM = 160;
export const CAPTION_BAND = 480;
