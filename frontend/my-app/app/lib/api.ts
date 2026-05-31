import type {
  Chapter, ContinueResponse, Novel, AIGeneration, PolishResponse,
  MemorySnapshot, CharacterMemory, CharacterState, WorldState,
  StyleProfile, NarrativeState, EmotionCurveSummary,
  StoryGraphData, Foreshadowing, StoryArc, WritingPlan,
  ConsistencyReport, PlanAnalysisResult, V4ContinueRequest, V4ContinueResponse,
} from "@/app/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(error || `HTTP ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// Novels
export async function listNovels(): Promise<{ novels: Novel[] }> {
  return request("/api/novels");
}

export async function createNovel(title: string): Promise<Novel> {
  return request("/api/novels", {
    method: "POST",
    body: JSON.stringify({ title }),
  });
}

export async function updateNovel(id: number, data: { title: string }): Promise<Novel> {
  return request(`/api/novels/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteNovel(id: number): Promise<void> {
  return request(`/api/novels/${id}`, { method: "DELETE" });
}

// Chapters
export async function listChapters(novelId: number): Promise<{ chapters: Chapter[] }> {
  return request(`/api/novels/${novelId}/chapters`);
}

export async function createChapter(novelId: number, title?: string): Promise<Chapter> {
  return request(`/api/novels/${novelId}/chapters`, {
    method: "POST",
    body: JSON.stringify({ title: title || "未命名章节" }),
  });
}

export async function getChapter(chapterId: number): Promise<Chapter> {
  return request(`/api/chapters/${chapterId}`);
}

export async function updateChapter(chapterId: number, data: { title?: string; content?: string }): Promise<Chapter> {
  return request(`/api/chapters/${chapterId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteChapter(chapterId: number): Promise<void> {
  return request(`/api/chapters/${chapterId}`, { method: "DELETE" });
}

// AI
export async function continueWriting(
  chapterId: number,
  userIntent: string,
  styleNote?: string,
  targetLength?: number
): Promise<ContinueResponse> {
  return request(`/api/chapters/${chapterId}/continue`, {
    method: "POST",
    body: JSON.stringify({
      user_intent: userIntent,
      style_note: styleNote || "",
      target_length: targetLength || 400,
    }),
  });
}

export async function regenerateWriting(
  chapterId: number,
  userIntent: string,
  styleNote?: string
): Promise<ContinueResponse> {
  return request(`/api/chapters/${chapterId}/regenerate`, {
    method: "POST",
    body: JSON.stringify({
      user_intent: userIntent,
      style_note: styleNote || "",
    }),
  });
}

export async function listGenerations(chapterId: number): Promise<{ generations: AIGeneration[] }> {
  return request(`/api/chapters/${chapterId}/generations`);
}

export async function polishText(
  chapterId: number,
  selectedText: string,
  contextBefore: string,
  contextAfter: string,
  requirement?: string
): Promise<PolishResponse> {
  return request(`/api/chapters/${chapterId}/polish`, {
    method: "POST",
    body: JSON.stringify({
      selected_text: selectedText,
      context_before: contextBefore,
      context_after: contextAfter,
      requirement: requirement || "",
    }),
  });
}

export async function acceptGeneration(generationId: number, accepted: boolean): Promise<AIGeneration> {
  return request(`/api/generations/${generationId}/accept`, {
    method: "PUT",
    body: JSON.stringify({ accepted }),
  });
}

// V2: Memory APIs

export async function getMemorySnapshot(novelId: number): Promise<MemorySnapshot> {
  return request(`/api/memory/novels/${novelId}/snapshot`);
}

export async function listCharacters(novelId: number): Promise<{ characters: CharacterMemory[] }> {
  return request(`/api/memory/novels/${novelId}/characters`);
}

export async function saveCharacter(
  novelId: number,
  characterName: string,
  memoryJson: CharacterState
): Promise<CharacterMemory> {
  return request(`/api/memory/novels/${novelId}/characters/${encodeURIComponent(characterName)}`, {
    method: "PUT",
    body: JSON.stringify({ memory_json: memoryJson }),
  });
}

export async function deleteCharacter(novelId: number, characterName: string): Promise<void> {
  return request(`/api/memory/novels/${novelId}/characters/${encodeURIComponent(characterName)}`, {
    method: "DELETE",
  });
}

export async function getWorldState(novelId: number): Promise<{ world_state: WorldState }> {
  return request(`/api/memory/novels/${novelId}/world`);
}

export async function saveWorldState(novelId: number, worldState: WorldState): Promise<{ world_state: WorldState }> {
  return request(`/api/memory/novels/${novelId}/world`, {
    method: "PUT",
    body: JSON.stringify({ world_state: worldState }),
  });
}

export async function updateChapterMemory(chapterId: number): Promise<void> {
  return request(`/api/chapters/${chapterId}/update-memory`, {
    method: "POST",
  });
}

// V3: Style APIs

export async function getStyleProfile(novelId: number): Promise<StyleProfile> {
  return request(`/api/novels/${novelId}/style-profile`);
}

export async function generateStyleProfile(novelId: number, force: boolean = false): Promise<StyleProfile> {
  return request(`/api/novels/${novelId}/style-profile`, {
    method: "POST",
    body: JSON.stringify({ force }),
  });
}

// V3: Narrative APIs

export async function getNarrativeState(chapterId: number): Promise<NarrativeState> {
  return request(`/api/chapters/${chapterId}/narrative-state`);
}

export async function listNarrativeStates(novelId: number): Promise<{ states: NarrativeState[] }> {
  return request(`/api/novels/${novelId}/narrative-states`);
}

export async function analyzeNarrativeState(chapterId: number): Promise<NarrativeState> {
  return request(`/api/chapters/${chapterId}/narrative-state`, { method: "POST" });
}

// V3: Emotion APIs

export async function getEmotionCurve(novelId: number): Promise<EmotionCurveSummary> {
  return request(`/api/novels/${novelId}/emotion-curve`);
}

// V3: Continue with full V3 context

export async function continueWritingV3(
  chapterId: number,
  userIntent: string,
  styleNote?: string,
  targetLength?: number
): Promise<ContinueResponse> {
  return request(`/api/chapters/${chapterId}/continue-v3`, {
    method: "POST",
    body: JSON.stringify({
      user_intent: userIntent,
      style_note: styleNote || "",
      target_length: targetLength || 400,
    }),
  });
}

// ---- V4 APIs ----

export async function continueWritingV4(
  chapterId: number,
  data: V4ContinueRequest
): Promise<V4ContinueResponse> {
  return request(`/api/chapters/${chapterId}/continue-v4`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getStoryGraph(novelId: number): Promise<StoryGraphData> {
  return request(`/api/novels/${novelId}/story-graph`);
}

export async function listForeshadowings(novelId: number): Promise<{ foreshadowings: Foreshadowing[] }> {
  return request(`/api/novels/${novelId}/foreshadowings`);
}

export async function createForeshadowing(novelId: number, data: Partial<Foreshadowing>): Promise<Foreshadowing> {
  return request(`/api/novels/${novelId}/foreshadowings`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateForeshadowing(id: number, data: Partial<Foreshadowing>): Promise<Foreshadowing> {
  return request(`/api/foreshadowings/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function listStoryArcs(novelId: number): Promise<{ arcs: StoryArc[] }> {
  return request(`/api/novels/${novelId}/story-arcs`);
}

export async function createStoryArc(novelId: number, data: Partial<StoryArc>): Promise<StoryArc> {
  return request(`/api/novels/${novelId}/story-arcs`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getWritingPlans(novelId: number): Promise<{ plans: WritingPlan[] }> {
  return request(`/api/novels/${novelId}/plans`);
}

export async function createWritingPlan(novelId: number, data: Record<string, unknown>): Promise<WritingPlan> {
  return request(`/api/novels/${novelId}/plans`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function autoAnalyzeNovel(novelId: number): Promise<PlanAnalysisResult> {
  return request(`/api/novels/${novelId}/auto-analyze`, { method: "POST" });
}

export async function getConsistencyCheck(chapterId: number): Promise<ConsistencyReport> {
  return request(`/api/chapters/${chapterId}/consistency-check`, { method: "POST" });
}

export async function getConsistencyHistory(novelId: number): Promise<{ reports: ConsistencyReport[] }> {
  return request(`/api/novels/${novelId}/consistency-history`);
}
