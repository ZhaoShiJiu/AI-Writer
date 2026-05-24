export interface Novel {
  id: number;
  title: string;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface Chapter {
  id: number;
  novel_id: number;
  title: string;
  content: string;
  summary: string | null;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface AIGeneration {
  id: number;
  chapter_id: number;
  user_intent: string | null;
  prompt_text: string;
  ai_output: string;
  accepted: boolean;
  created_at: string;
}

export interface ContinueResponse {
  generation_id: number;
  ai_output: string;
}
