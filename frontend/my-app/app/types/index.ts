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

export interface PolishResponse {
  generation_id: number;
  polished_output: string;
}

// V2: Memory types

export interface CharacterMemory {
  id: number;
  novel_id: number;
  character_name: string;
  memory_json: CharacterState;
  created_at: string;
  updated_at: string;
}

export interface CharacterState {
  name?: string;
  realm?: string;
  personality?: string[];
  relationships?: { target: string; relation: string }[];
  notes?: string;
}

export interface WorldState {
  major_factions?: string[];
  world_rules?: string[];
  current_conflicts?: string[];
  locations?: { name: string; description: string }[];
  notes?: string;
}

export interface WorldMemory {
  id: number;
  novel_id: number;
  world_state: WorldState;
  created_at: string;
  updated_at: string;
}

export interface MemorySnapshot {
  characters: CharacterMemory[];
  world: WorldMemory | null;
}

export interface SummaryItem {
  id: number;
  chapter_id: number | null;
  summary: string;
  characters: string[];
  important_events: string[];
  emotion: string | null;
  foreshadowing: string[];
}

// V3: Style types

export interface StyleProfile {
  id: number;
  novel_id: number;
  style_json: StyleProfileData;
  updated_at: string;
}

export interface StyleProfileData {
  sentence_length: { average: string; variance: string };
  dialogue_ratio: number;
  emotion_density: { primary_emotions: string[]; density: string };
  description_density: string;
  pace: string;
  preferred_tone: string;
  common_expressions: string[];
  stylistic_notes: string;
  sentence_patterns: string[];
}

// V3: Narrative types

export interface NarrativeState {
  id: number;
  novel_id: number;
  chapter_id: number;
  scene_type: string | null;
  tension_score: number;
  emotion: string | null;
  pace: string;
  goal: string | null;
  emotional_curve: EmotionCurvePoint[];
  narrative_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface EmotionCurvePoint {
  position: number;
  emotion: string;
  intensity: number;
}

export interface EmotionCurveSummary {
  novel_id: number;
  curve: EmotionCurveSummaryPoint[];
}

export interface EmotionCurveSummaryPoint {
  chapter_id: number;
  chapter_title: string;
  chapter_position: number;
  emotion: string | null;
  tension_score: number;
}

// ---- V4 Types ----

export interface StoryGraphNode {
  id: string;
  label: string;
  node_type: "character" | "event" | "location" | "faction";
  properties: Record<string, unknown>;
}

export interface StoryGraphEdge {
  source: string;
  target: string;
  edge_type: string;
  properties: Record<string, unknown>;
}

export interface StoryGraphData {
  nodes: StoryGraphNode[];
  edges: StoryGraphEdge[];
}

export interface Foreshadowing {
  id: number;
  novel_id: number;
  name: string;
  description: string | null;
  planted_at_chapter_id: number | null;
  payoff_at_chapter_id: number | null;
  status: "planned" | "planted" | "reminded" | "payoff";
  content_snippet: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface StoryArc {
  id: number;
  novel_id: number;
  title: string;
  arc_type: string;
  description: string | null;
  start_chapter_id: number | null;
  end_chapter_id: number | null;
  status: string;
  emotional_target: Record<string, unknown> | null;
  pacing_plan: Record<string, unknown> | null;
  scene_plan: Record<string, unknown> | null;
}

export interface WritingPlan {
  id: number;
  novel_id: number;
  chapter_id: number | null;
  plan_json: PlanData;
  plan_type: string;
  created_at: string;
  updated_at: string;
}

export interface PlanData {
  genre?: string;
  themes?: string[];
  main_characters?: string[];
  scene_plan?: ScenePlanItem[];
  overall_arc_type?: string;
  theme_notes?: string;
}

export interface ScenePlanItem {
  position: number;
  goal: string;
  expected_emotion: string;
  scene_type: string;
  conflict_points: string[];
  characters_involved: string[];
  estimated_length: number;
  key_beats?: string[];
}

export interface ConsistencyIssue {
  severity: "critical" | "major" | "minor";
  category: string;
  description: string;
  suggestion: string;
}

export interface ConsistencyReport {
  passed: boolean;
  issues: ConsistencyIssue[];
  overall_score: number;
  check_type: string;
}

export interface V4WorkflowStatus {
  current_step: string;
  progress: number;
  steps: string[];
  step_results?: Record<string, unknown>;
  generated_text: string | null;
  generation_id: number | null;
  error: string | null;
}

export interface V4ContinueRequest {
  user_intent?: string;
  style_note?: string;
  target_length?: number;
  emotion_target?: string;
  pace_target?: string;
  planner_input?: PlanData;
}

export interface V4ContinueResponse {
  generation_id: number;
  ai_output: string;
  workflow_status?: V4WorkflowStatus;
}

export interface PlanAnalysisResult {
  genre: string;
  themes: string[];
  main_characters: string[];
  narrative_structure: string;
  suggested_arcs: Record<string, unknown>[];
  analysis_notes: string;
}

