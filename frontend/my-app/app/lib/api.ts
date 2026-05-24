import type { Chapter, ContinueResponse, Novel, AIGeneration } from "@/app/types";

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

export async function acceptGeneration(generationId: number, accepted: boolean): Promise<AIGeneration> {
  return request(`/api/generations/${generationId}/accept`, {
    method: "PUT",
    body: JSON.stringify({ accepted }),
  });
}
