"use client";
import { useState } from "react";
import { useNovelStore } from "@/app/store/useNovelStore";

export default function StylePanel() {
  const { currentNovelId, styleProfile, generateStyleProfile, loadStyleProfile } =
    useNovelStore();
  const [expanded, setExpanded] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  const handleAnalyze = async () => {
    if (!currentNovelId) return;
    setAnalyzing(true);
    await generateStyleProfile(currentNovelId);
    setAnalyzing(false);
  };

  if (!currentNovelId) {
    return (
      <div className="border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800/50"
        >
          <h2 className="text-sm font-semibold text-purple-500 uppercase tracking-wider">
            V3 风格分析
          </h2>
          <span className="text-xs text-gray-400">{expanded ? "收起" : "展开"}</span>
        </button>
        {expanded && (
          <div className="px-4 pb-4">
            <p className="text-xs text-gray-400">请先选择小说</p>
          </div>
        )}
      </div>
    );
  }

  const hasProfile =
    styleProfile && styleProfile.style_json && Object.keys(styleProfile.style_json).length > 0;
  const sj = hasProfile ? styleProfile!.style_json : null;

  return (
    <div className="border-b border-gray-200 dark:border-gray-700">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800/50"
      >
        <h2 className="text-sm font-semibold text-purple-500 uppercase tracking-wider">
          V3 风格分析
        </h2>
        <span className="text-xs text-gray-400">{expanded ? "收起" : "展开"}</span>
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-3 max-h-80 overflow-y-auto">
          {!hasProfile ? (
            <div>
              <p className="text-xs text-gray-400 mb-2">
                暂无风格分析数据，点击下方按钮使用 AI 分析
              </p>
              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="w-full py-1.5 px-3 bg-purple-500 hover:bg-purple-600 disabled:bg-purple-300 text-white rounded text-xs font-medium transition-colors"
              >
                {analyzing ? "分析中..." : "分析风格"}
              </button>
            </div>
          ) : (
            <>
              {/* Sentence style */}
              <div>
                <h3 className="text-xs font-medium text-gray-500 mb-1">句式风格</h3>
                <div className="flex gap-1.5 flex-wrap">
                  <span className="px-1.5 py-0.5 bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 rounded text-xs">
                    {sj?.sentence_length?.average || "中等"}句
                  </span>
                  <span className="px-1.5 py-0.5 bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 rounded text-xs">
                    变化度{sj?.sentence_length?.variance || "中等"}
                  </span>
                </div>
              </div>

              {/* Dialogue ratio */}
              <div>
                <h3 className="text-xs font-medium text-gray-500 mb-1">
                  对话比例
                  <span className="ml-1 text-purple-500">
                    {sj?.dialogue_ratio != null
                      ? `${Math.round(sj.dialogue_ratio * 100)}%`
                      : "未知"}
                  </span>
                </h3>
                <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-purple-500 rounded-full transition-all"
                    style={{ width: `${(sj?.dialogue_ratio || 0) * 100}%` }}
                  />
                </div>
              </div>

              {/* Description density */}
              <div>
                <h3 className="text-xs font-medium text-gray-500 mb-1">描写密度</h3>
                <span className="px-1.5 py-0.5 bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 rounded text-xs">
                  {sj?.description_density || "未知"}
                </span>
              </div>

              {/* Pace */}
              <div>
                <h3 className="text-xs font-medium text-gray-500 mb-1">叙事节奏</h3>
                <span className="px-1.5 py-0.5 bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 rounded text-xs">
                  {sj?.pace === "fast"
                    ? "快节奏"
                    : sj?.pace === "slow"
                      ? "慢节奏"
                      : "中等节奏"}
                </span>
              </div>

              {/* Tone */}
              <div>
                <h3 className="text-xs font-medium text-gray-500 mb-1">偏好基调</h3>
                <span className="px-1.5 py-0.5 bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 rounded text-xs">
                  {sj?.preferred_tone || "未知"}
                </span>
              </div>

              {/* Emotion density */}
              {sj?.emotion_density?.primary_emotions && (
                <div>
                  <h3 className="text-xs font-medium text-gray-500 mb-1">
                    情绪密度（{sj?.emotion_density?.density || "未知"}）
                  </h3>
                  <div className="flex gap-1 flex-wrap">
                    {sj.emotion_density.primary_emotions.map((em: string) => (
                      <span
                        key={em}
                        className="px-1.5 py-0.5 bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 rounded text-xs"
                      >
                        {em}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Stylistic notes */}
              {sj?.stylistic_notes && (
                <div>
                  <h3 className="text-xs font-medium text-gray-500 mb-1">风格备注</h3>
                  <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
                    {sj.stylistic_notes}
                  </p>
                </div>
              )}

              {/* Re-analyze button */}
              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="w-full py-1.5 px-3 border border-purple-300 dark:border-purple-700 text-purple-500 hover:bg-purple-50 dark:hover:bg-purple-900/20 rounded text-xs font-medium transition-colors"
              >
                {analyzing ? "分析中..." : "重新分析"}
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
