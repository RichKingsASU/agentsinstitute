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
};

export type Manifest = {
  epId: string;
  title: string;
  scenes: Scene[];
};
