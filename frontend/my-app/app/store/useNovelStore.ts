import { create } from "zustand";
import type { Chapter, Novel, AIGeneration } from "@/app/types";
import * as api from "@/app/lib/api";

interface NovelState {
  // Data
  novels: Novel[];
  currentNovelId: number | null;
  chapters: Chapter[];
  currentChapterId: number | null;
  currentChapter: Chapter | null;
  generations: AIGeneration[];
  aiOutput: string | null;
  generationId: number | null;

  // UI state
  loading: boolean;
  generating: boolean;
  error: string | null;

  // Novel actions
  loadNovels: () => Promise<void>;
  createNovel: (title: string) => Promise<Novel | null>;
  selectNovel: (novelId: number) => Promise<void>;
  deleteNovel: (novelId: number) => Promise<void>;

  // Chapter actions
  loadChapters: (novelId: number) => Promise<void>;
  createChapter: (novelId: number, title?: string) => Promise<Chapter | null>;
  selectChapter: (chapterId: number) => Promise<void>;
  saveChapter: (content: string) => Promise<void>;
  deleteChapter: (chapterId: number) => Promise<void>;

  // AI actions
  continueWriting: (userIntent: string, styleNote?: string) => Promise<void>;
  regenerateWriting: (userIntent: string, styleNote?: string) => Promise<void>;
  loadGenerations: (chapterId: number) => Promise<void>;
  acceptGeneration: (generationId: number, accepted: boolean) => Promise<void>;

  // Utils
  clearError: () => void;
  clearAiOutput: () => void;
}

export const useNovelStore = create<NovelState>((set, get) => ({
  novels: [],
  currentNovelId: null,
  chapters: [],
  currentChapterId: null,
  currentChapter: null,
  generations: [],
  aiOutput: null,
  generationId: null,
  loading: false,
  generating: false,
  error: null,

  async loadNovels() {
    set({ loading: true, error: null });
    try {
      const data = await api.listNovels();
      set({ novels: data.novels, loading: false });
    } catch (e: any) {
      set({ error: e.message, loading: false });
    }
  },

  async createNovel(title: string) {
    try {
      const novel = await api.createNovel(title);
      set((s) => ({ novels: [novel, ...s.novels] }));
      return novel;
    } catch (e: any) {
      set({ error: e.message });
      return null;
    }
  },

  async selectNovel(novelId: number) {
    set({ currentNovelId: novelId, currentChapterId: null, currentChapter: null, aiOutput: null });
    await get().loadChapters(novelId);
  },

  async deleteNovel(novelId: number) {
    try {
      await api.deleteNovel(novelId);
      set((s) => ({
        novels: s.novels.filter((n) => n.id !== novelId),
        currentNovelId: s.currentNovelId === novelId ? null : s.currentNovelId,
        chapters: s.currentNovelId === novelId ? [] : s.chapters,
        currentChapterId: s.currentNovelId === novelId ? null : s.currentChapterId,
        currentChapter: s.currentNovelId === novelId ? null : s.currentChapter,
      }));
    } catch (e: any) {
      set({ error: e.message });
    }
  },

  async loadChapters(novelId: number) {
    set({ loading: true });
    try {
      const data = await api.listChapters(novelId);
      set({ chapters: data.chapters, loading: false });
    } catch (e: any) {
      set({ error: e.message, loading: false });
    }
  },

  async createChapter(novelId: number, title?: string) {
    try {
      const chapter = await api.createChapter(novelId, title);
      set((s) => ({ chapters: [...s.chapters, chapter] }));
      return chapter;
    } catch (e: any) {
      set({ error: e.message });
      return null;
    }
  },

  async selectChapter(chapterId: number) {
    set({ loading: true, aiOutput: null });
    try {
      const chapter = await api.getChapter(chapterId);
      set({
        currentChapterId: chapterId,
        currentChapter: chapter,
        loading: false,
      });
      await get().loadGenerations(chapterId);
    } catch (e: any) {
      set({ error: e.message, loading: false });
    }
  },

  async saveChapter(content: string) {
    const { currentChapterId } = get();
    if (!currentChapterId) return;
    try {
      const chapter = await api.updateChapter(currentChapterId, { content });
      set({ currentChapter: chapter });
    } catch (e: any) {
      set({ error: e.message });
    }
  },

  async deleteChapter(chapterId: number) {
    try {
      await api.deleteChapter(chapterId);
      set((s) => ({
        chapters: s.chapters.filter((c) => c.id !== chapterId),
        currentChapterId: s.currentChapterId === chapterId ? null : s.currentChapterId,
        currentChapter: s.currentChapterId === chapterId ? null : s.currentChapter,
        generations: [],
        aiOutput: null,
      }));
    } catch (e: any) {
      set({ error: e.message });
    }
  },

  async continueWriting(userIntent: string, styleNote?: string) {
    const { currentChapterId } = get();
    if (!currentChapterId) return;
    set({ generating: true, error: null });
    try {
      const data = await api.continueWriting(currentChapterId, userIntent, styleNote);
      set({ aiOutput: data.ai_output, generationId: data.generation_id, generating: false });
    } catch (e: any) {
      set({ error: e.message, generating: false });
    }
  },

  async regenerateWriting(userIntent: string, styleNote?: string) {
    const { currentChapterId } = get();
    if (!currentChapterId) return;
    set({ generating: true, error: null });
    try {
      const data = await api.regenerateWriting(currentChapterId, userIntent, styleNote);
      set({ aiOutput: data.ai_output, generationId: data.generation_id, generating: false });
    } catch (e: any) {
      set({ error: e.message, generating: false });
    }
  },

  async loadGenerations(chapterId: number) {
    try {
      const data = await api.listGenerations(chapterId);
      set({ generations: data.generations });
    } catch (e: any) {
      // silently fail for history
    }
  },

  async acceptGeneration(generationId: number, accepted: boolean) {
    try {
      await api.acceptGeneration(generationId, accepted);
      set((s) => ({
        generations: s.generations.map((g) =>
          g.id === generationId ? { ...g, accepted } : g
        ),
      }));
    } catch (e: any) {
      // silently fail
    }
  },

  clearError() {
    set({ error: null });
  },

  clearAiOutput() {
    set({ aiOutput: null, generationId: null });
  },
}));
