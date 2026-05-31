"use client";
import { useState, useEffect } from "react";
import { useNovelStore } from "@/app/store/useNovelStore";
import type { NarrativeState } from "@/app/types";
import * as api from "@/app/lib/api";

const EMOTION_COLORS: Record<string, string> = {
  压抑: "#6b7280",
  紧张: "#ef4444",
  热血: "#f97316",
  悲凉: "#3b82f6",
  温情: "#f59e0b",
  冷幽默: "#06b6d4",
  恐惧: "#7c3aed",
  平静: "#22c55e",
  愤怒: "#dc2626",
  惊喜: "#ec4899",
  忧伤: "#6366f1",
};

function emotionColor(emotion: string | null): string {
  return EMOTION_COLORS[emotion || ""] || "#9ca3af";
}

function paceLabel(pace: string): string {
  if (pace === "fast") return "快节奏";
  if (pace === "slow") return "慢节奏";
  return "中等节奏";
}

export default function NarrativePanel() {
  const { currentNovelId, currentChapterId, currentNarrativeState, narrativeStates, loadNarrativeStates } =
    useNovelStore();
  const [expanded, setExpanded] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [selectedChapterNarrative, setSelectedChapterNarrative] =
    useState<NarrativeState | null>(null);

  useEffect(() => {
    if (currentNovelId) {
      loadNarrativeStates(currentNovelId);
    }
  }, [currentNovelId]);

  const handleAnalyze = async () => {
    if (!currentChapterId) return;
    setAnalyzing(true);
    try {
      await api.analyzeNarrativeState(currentChapterId);
      if (currentNovelId) {
        await loadNarrativeStates(currentNovelId);
      }
    } catch {
      // silently fail
    }
    setAnalyzing(false);
  };

  if (!currentNovelId) {
    return (
      <div className="border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800/50"
        >
          <h2 className="text-sm font-semibold text-indigo-500 uppercase tracking-wider">
            V3 叙事曲线
          </h2>
          <span className="text-xs text-gray-400">{expanded ? "收起" : "展开"}</span>
        </button>
      </div>
    );
  }

  const maxTension = Math.max(1, ...narrativeStates.map((s) => s.tension_score));

  return (
    <div className="border-b border-gray-200 dark:border-gray-700">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800/50"
      >
        <h2 className="text-sm font-semibold text-indigo-500 uppercase tracking-wider">
          V3 叙事曲线
        </h2>
        <span className="text-xs text-gray-400">{expanded ? "收起" : "展开"}</span>
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-4 max-h-96 overflow-y-auto">
          {/* Current Narrative State (inline badge) */}
          {currentNarrativeState && (
            <div className="p-2 bg-indigo-50 dark:bg-indigo-900/20 rounded">
              <h3 className="text-xs font-medium text-indigo-600 dark:text-indigo-400 mb-1.5">
                当前叙事状态
              </h3>
              <div className="flex gap-1 flex-wrap">
                {currentNarrativeState.scene_type && (
                  <span className="px-1.5 py-0.5 bg-white dark:bg-gray-800 text-indigo-600 dark:text-indigo-400 rounded text-xs">
                    {currentNarrativeState.scene_type}
                  </span>
                )}
                <span className="px-1.5 py-0.5 bg-white dark:bg-gray-800 text-indigo-600 dark:text-indigo-400 rounded text-xs">
                  张力 {currentNarrativeState.tension_score}
                </span>
                {currentNarrativeState.emotion && (
                  <span className="px-1.5 py-0.5 bg-white dark:bg-gray-800 text-indigo-600 dark:text-indigo-400 rounded text-xs">
                    {currentNarrativeState.emotion}
                  </span>
                )}
                <span className="px-1.5 py-0.5 bg-white dark:bg-gray-800 text-indigo-600 dark:text-indigo-400 rounded text-xs">
                  {paceLabel(currentNarrativeState.pace)}
                </span>
              </div>
              {currentNarrativeState.goal && (
                <p className="text-xs text-gray-500 mt-1.5">
                  目标：{currentNarrativeState.goal}
                </p>
              )}
            </div>
          )}

          {/* Emotion Curve Visualization */}
          {narrativeStates.length > 0 ? (
            <div>
              <h3 className="text-xs font-medium text-gray-500 mb-2">情绪曲线</h3>
              {/* Tension Bars */}
              <div className="space-y-1.5">
                {narrativeStates.map((ns) => (
                  <button
                    key={ns.id}
                    onClick={() =>
                      setSelectedChapterNarrative(
                        selectedChapterNarrative?.id === ns.id ? null : ns
                      )
                    }
                    className="w-full text-left group"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500 w-16 truncate">
                        {ns.chapter_id}
                      </span>
                      <div className="flex-1 h-4 bg-gray-100 dark:bg-gray-800 rounded-sm overflow-hidden relative">
                        <div
                          className="h-full rounded-sm transition-all"
                          style={{
                            width: `${(ns.tension_score / maxTension) * 100}%`,
                            backgroundColor: emotionColor(ns.emotion),
                          }}
                        />
                      </div>
                      <span className="text-xs text-gray-400 w-8 text-right">
                        {ns.tension_score}
                      </span>
                    </div>

                    {/* Expanded detail */}
                    {selectedChapterNarrative?.id === ns.id && (
                      <div className="mt-1.5 ml-18 p-2 bg-gray-50 dark:bg-gray-800 rounded text-xs space-y-0.5">
                        {ns.scene_type && (
                          <div className="text-gray-600 dark:text-gray-400">
                            场景：{ns.scene_type}
                          </div>
                        )}
                        {ns.emotion && (
                          <div className="text-gray-600 dark:text-gray-400">
                            情绪：{ns.emotion}
                          </div>
                        )}
                        <div className="text-gray-600 dark:text-gray-400">
                          节奏：{paceLabel(ns.pace)}
                        </div>
                        {ns.goal && (
                          <div className="text-gray-600 dark:text-gray-400">
                            目标：{ns.goal}
                          </div>
                        )}
                        {ns.narrative_json &&
                          typeof (ns.narrative_json as Record<string, unknown>).narrative_notes === "string" && (
                            <div className="text-gray-500 dark:text-gray-500 italic">
                              {(ns.narrative_json as Record<string, unknown>)
                                .narrative_notes as string}
                            </div>
                          )}
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-xs text-gray-400">
              暂无叙事状态数据，保存章节后自动分析
            </p>
          )}

          {/* Manual analyze button */}
          {currentChapterId && (
            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="w-full py-1.5 px-3 border border-indigo-300 dark:border-indigo-700 text-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded text-xs font-medium transition-colors disabled:opacity-50"
            >
              {analyzing ? "分析中..." : "分析当前章节"}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
