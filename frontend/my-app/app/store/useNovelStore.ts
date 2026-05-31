import { create } from "zustand";
import type { Chapter, Novel, AIGeneration, StyleProfile, NarrativeState, EmotionCurveSummaryPoint } from "@/app/types";
import type { Editor } from "@tiptap/react";
import * as api from "@/app/lib/api";

let editorInstance: Editor | null = null;

export function setEditorInstance(editor: Editor | null) {
  editorInstance = editor;
}

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

  // Selection
  selectedText: string;
  selectionFrom: number;
  selectionTo: number;
  contextBefore: string;
  contextAfter: string;

  // Polish
  polishing: boolean;
  polishedOutput: string | null;
  polishGenerationId: number | null;
  polishMode: boolean;

  // V3: Style & Narrative state
  styleProfile: StyleProfile | null;
  narrativeStates: NarrativeState[];
  currentNarrativeState: NarrativeState | null;
  emotionCurve: EmotionCurveSummaryPoint[];
  v3Mode: boolean;

  // UI state
  loading: boolean;
  generating: boolean;
  error: string | null;

  // Novel actions
  loadNovels: () => Promise<void>;
  createNovel: (title: string) => Promise<Novel | null>;
  selectNovel: (novelId: number) => Promise<void>;
  updateNovelTitle: (novelId: number, title: string) => Promise<void>;
  deleteNovel: (novelId: number) => Promise<void>;

  // Chapter actions
  loadChapters: (novelId: number) => Promise<void>;
  createChapter: (novelId: number, title?: string) => Promise<Chapter | null>;
  selectChapter: (chapterId: number) => Promise<void>;
  updateChapterTitle: (chapterId: number, title: string) => Promise<void>;
  saveChapter: (content: string) => Promise<void>;
  deleteChapter: (chapterId: number) => Promise<void>;

  // Selection actions
  setSelection: (text: string, from: number, to: number, before: string, after: string) => void;
  clearSelection: () => void;

  // AI actions
  continueWriting: (userIntent: string, styleNote?: string) => Promise<void>;
  regenerateWriting: (userIntent: string, styleNote?: string) => Promise<void>;
  loadGenerations: (chapterId: number) => Promise<void>;
  acceptGeneration: (generationId: number, accepted: boolean) => Promise<void>;

  // Polish actions
  polishText: (requirement: string) => Promise<void>;
  acceptPolish: () => void;
  rejectPolish: () => void;
  setPolishMode: (active: boolean) => void;

  // V3: Style & Narrative actions
  loadStyleProfile: (novelId: number) => Promise<void>;
  generateStyleProfile: (novelId: number) => Promise<void>;
  loadCurrentNarrativeState: (chapterId: number) => Promise<void>;
  loadNarrativeStates: (novelId: number) => Promise<void>;
  loadEmotionCurve: (novelId: number) => Promise<void>;
  continueWritingV3: (userIntent: string, styleNote?: string) => Promise<void>;
  setV3Mode: (active: boolean) => void;

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
  selectedText: "",
  selectionFrom: 0,
  selectionTo: 0,
  contextBefore: "",
  contextAfter: "",
  polishing: false,
  polishedOutput: null,
  polishGenerationId: null,
  polishMode: false,
  styleProfile: null,
  narrativeStates: [],
  currentNarrativeState: null,
  emotionCurve: [],
  v3Mode: false,
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
    // V3: 自动加载风格画像和情绪曲线
    get().loadStyleProfile(novelId);
    get().loadEmotionCurve(novelId);
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

  async updateNovelTitle(novelId: number, title: string) {
    try {
      const novel = await api.updateNovel(novelId, { title });
      set((s) => ({
        novels: s.novels.map((n) => (n.id === novelId ? novel : n)),
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
      // V3: 自动加载叙事状态
      get().loadCurrentNarrativeState(chapterId);
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

  async updateChapterTitle(chapterId: number, title: string) {
    try {
      const chapter = await api.updateChapter(chapterId, { title });
      set((s) => ({
        chapters: s.chapters.map((c) => (c.id === chapterId ? { ...c, title: chapter.title } : c)),
        currentChapter: s.currentChapter?.id === chapterId ? { ...s.currentChapter, title: chapter.title } : s.currentChapter,
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

  // Selection actions
  setSelection(text: string, from: number, to: number, before: string, after: string) {
    set({ selectedText: text, selectionFrom: from, selectionTo: to, contextBefore: before, contextAfter: after });
  },

  clearSelection() {
    set({ selectedText: "", selectionFrom: 0, selectionTo: 0, contextBefore: "", contextAfter: "" });
  },

  // Polish actions
  async polishText(requirement: string) {
    const { currentChapterId, selectedText, contextBefore, contextAfter } = get();
    if (!currentChapterId || !selectedText) return;
    set({ polishing: true, error: null });
    try {
      const data = await api.polishText(currentChapterId, selectedText, contextBefore, contextAfter, requirement);
      set({ polishedOutput: data.polished_output, polishGenerationId: data.generation_id, polishing: false });
    } catch (e: any) {
      set({ error: e.message, polishing: false });
    }
  },

  acceptPolish() {
    const { polishedOutput, selectionFrom, selectionTo } = get();
    if (!polishedOutput || !editorInstance) return;

    editorInstance
      .chain()
      .focus()
      .insertContentAt({ from: selectionFrom, to: selectionTo }, polishedOutput)
      .run();

    set({ polishedOutput: null, polishGenerationId: null, polishMode: false });
    get().clearSelection();
  },

  rejectPolish() {
    set({ polishedOutput: null, polishGenerationId: null, polishMode: false });
  },

  setPolishMode(active: boolean) {
    set({ polishMode: active });
  },

  // V3: Style & Narrative actions
  async loadStyleProfile(novelId: number) {
    try {
      const profile = await api.getStyleProfile(novelId);
      if (profile.id !== 0) {
        set({ styleProfile: profile });
      }
    } catch {
      // silently fail
    }
  },

  async generateStyleProfile(novelId: number) {
    try {
      const profile = await api.generateStyleProfile(novelId, true);
      set({ styleProfile: profile });
    } catch {
      // silently fail
    }
  },

  async loadCurrentNarrativeState(chapterId: number) {
    try {
      const state = await api.getNarrativeState(chapterId);
      if (state.id !== 0) {
        set({ currentNarrativeState: state });
      } else {
        set({ currentNarrativeState: null });
      }
    } catch {
      set({ currentNarrativeState: null });
    }
  },

  async loadNarrativeStates(novelId: number) {
    try {
      const data = await api.listNarrativeStates(novelId);
      set({ narrativeStates: data.states });
    } catch {
      // silently fail
    }
  },

  async loadEmotionCurve(novelId: number) {
    try {
      const data = await api.getEmotionCurve(novelId);
      set({ emotionCurve: data.curve });
    } catch {
      // silently fail
    }
  },

  async continueWritingV3(userIntent: string, styleNote?: string) {
    const { currentChapterId } = get();
    if (!currentChapterId) return;
    set({ generating: true, error: null });
    try {
      const data = await api.continueWritingV3(
        currentChapterId,
        userIntent,
        styleNote,
      );
      set({
        aiOutput: data.ai_output,
        generationId: data.generation_id,
        generating: false,
      });
    } catch (e: any) {
      set({ error: e.message, generating: false });
    }
  },

  setV3Mode(active: boolean) {
    set({ v3Mode: active });
  },

  clearError() {
    set({ error: null });
  },

  clearAiOutput() {
    set({ aiOutput: null, generationId: null });
  },
}));
