"use client";

import { useState } from "react";
import { useNovelStore } from "@/app/store/useNovelStore";

export default function AIPanel() {
  const {
    currentChapter,
    aiOutput,
    generationId,
    generating,
    continueWriting,
    regenerateWriting,
    continueWritingV3,
    clearAiOutput,
    saveChapter,
    acceptGeneration,
    selectedText,
    polishing,
    polishedOutput,
    polishMode,
    polishText,
    acceptPolish,
    rejectPolish,
    error,
    v3Mode,
    setV3Mode,
    currentNarrativeState,
    styleProfile,
  } = useNovelStore();

  const [userIntent, setUserIntent] = useState("");
  const [styleNote, setStyleNote] = useState("");
  const [polishRequirement, setPolishRequirement] = useState("");
  // V3 controls
  const [emotionTarget, setEmotionTarget] = useState("延续当前");
  const [paceControl, setPaceControl] = useState("保持当前");

  const handleContinue = async () => {
    if (!currentChapter) return;
    if (v3Mode) {
      await continueWritingV3(userIntent, styleNote);
    } else {
      await continueWriting(userIntent, styleNote);
    }
  };

  const handleRegenerate = async () => {
    if (!currentChapter) return;
    if (v3Mode) {
      await continueWritingV3(userIntent, styleNote);
    } else {
      await regenerateWriting(userIntent, styleNote);
    }
  };

  const handleAccept = async () => {
    if (!currentChapter || !aiOutput) return;

    const currentContent = currentChapter.content || "";
    const newContent = currentContent + "\n\n" + aiOutput;
    await saveChapter(newContent);

    if (generationId) {
      await acceptGeneration(generationId, true);
    }

    clearAiOutput();
    setUserIntent("");
  };

  const handleReject = async () => {
    if (generationId) {
      await acceptGeneration(generationId, false);
    }
    clearAiOutput();
  };

  const handlePolish = async () => {
    await polishText(polishRequirement);
  };

  const handleAcceptPolish = async () => {
    acceptPolish();
    setPolishRequirement("");
  };

  const handleCancelPolish = () => {
    rejectPolish();
    setPolishRequirement("");
  };

  return (
    <aside className="flex-1 overflow-hidden flex flex-col">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">AI 协同创作</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {!currentChapter ? (
          <p className="text-sm text-gray-400">请先选择要续写的章节</p>
        ) : polishMode ? (
          <>
            {/* Polish Mode Banner */}
            <div className="flex items-center gap-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded text-xs text-blue-600 dark:text-blue-400">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
              </svg>
              润色模式
              <span className="flex-1" />
              <button
                onClick={handleCancelPolish}
                className="text-blue-500 hover:text-blue-700 dark:hover:text-blue-300"
              >
                ✕ 退出
              </button>
            </div>

            {/* Selected text preview */}
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">选中文本</label>
              <div className="w-full px-3 py-2 text-sm border rounded border-blue-300 dark:border-blue-600 bg-blue-50/50 dark:bg-blue-900/10 text-gray-700 dark:text-gray-300 max-h-32 overflow-y-auto whitespace-pre-wrap leading-relaxed">
                {selectedText}
              </div>
            </div>

            {/* Polish requirement */}
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">润色要求（可选）</label>
              <textarea
                value={polishRequirement}
                onChange={(e) => setPolishRequirement(e.target.value)}
                placeholder='例如："更有文采""更简洁""更有压迫感"'
                rows={2}
                className="w-full px-3 py-2 text-sm border rounded border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 resize-none"
              />
            </div>

            {/* Polish button */}
            <button
              onClick={handlePolish}
              disabled={polishing || !selectedText}
              className="w-full py-2 px-4 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white rounded-md text-sm font-medium transition-colors"
            >
              {polishing ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                  润色中...
                </span>
              ) : (
                "开始润色"
              )}
            </button>

            {error && (
              <p className="text-sm text-red-500 p-2 bg-red-50 dark:bg-red-900/20 rounded">{error}</p>
            )}

            {/* Polished Output */}
            {polishedOutput && (
              <div className="space-y-3">
                <div className="border border-green-300 dark:border-green-700 bg-green-50 dark:bg-green-900/20 rounded-md p-3">
                  <h4 className="text-xs font-medium text-green-600 dark:text-green-400 mb-2">润色结果</h4>
                  <div className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed max-h-80 overflow-y-auto">
                    {polishedOutput}
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={handleAcceptPolish}
                    className="flex-1 py-1.5 px-3 bg-green-500 hover:bg-green-600 text-white rounded text-xs font-medium transition-colors"
                  >
                    替换原文
                  </button>
                  <button
                    onClick={handleCancelPolish}
                    className="flex-1 py-1.5 px-3 bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-200 rounded text-xs font-medium transition-colors"
                  >
                    取消
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          <>
            {/* V2/V3 Toggle */}
            <div className="flex items-center gap-2 p-2 bg-purple-50 dark:bg-purple-900/20 rounded">
              <span className="text-xs font-medium text-purple-600 dark:text-purple-400">
                V3 智能模式
              </span>
              <button
                onClick={() => setV3Mode(!v3Mode)}
                className={`relative w-10 h-5 rounded-full transition-colors ${
                  v3Mode
                    ? "bg-purple-500"
                    : "bg-gray-300 dark:bg-gray-600"
                }`}
              >
                <span
                  className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
                    v3Mode ? "translate-x-5" : "translate-x-0.5"
                  }`}
                />
              </button>
              <span className="text-xs text-gray-400 flex-1 text-right">
                {v3Mode ? "风格+叙事" : "标准"}
              </span>
            </div>

            {/* V3 Controls */}
            {v3Mode && (
              <div className="space-y-3 p-2 bg-purple-50/50 dark:bg-purple-900/10 rounded border border-purple-200 dark:border-purple-800">
                {/* Narrative state indicator */}
                {currentNarrativeState && (
                  <div className="flex gap-1 flex-wrap">
                    {currentNarrativeState.scene_type && (
                      <span className="px-1.5 py-0.5 bg-white dark:bg-gray-800 text-purple-600 dark:text-purple-400 rounded text-xs">
                        {currentNarrativeState.scene_type}
                      </span>
                    )}
                    <span className="px-1.5 py-0.5 bg-white dark:bg-gray-800 text-purple-600 dark:text-purple-400 rounded text-xs">
                      张力 {currentNarrativeState.tension_score}
                    </span>
                    {currentNarrativeState.emotion && (
                      <span className="px-1.5 py-0.5 bg-white dark:bg-gray-800 text-purple-600 dark:text-purple-400 rounded text-xs">
                        {currentNarrativeState.emotion}
                      </span>
                    )}
                  </div>
                )}

                {/* Style indicator */}
                {styleProfile?.style_json?.preferred_tone && (
                  <div className="text-xs text-purple-500">
                    风格基调：{styleProfile.style_json.preferred_tone}
                    {styleProfile.style_json.pace &&
                      ` · ${styleProfile.style_json.pace === "fast" ? "快" : styleProfile.style_json.pace === "slow" ? "慢" : "中"}节奏`}
                  </div>
                )}

                {/* Emotion target */}
                <div>
                  <label className="block text-xs font-medium text-purple-500 mb-1">
                    情绪目标
                  </label>
                  <select
                    value={emotionTarget}
                    onChange={(e) => setEmotionTarget(e.target.value)}
                    className="w-full px-2 py-1 text-xs border rounded border-purple-300 dark:border-purple-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300"
                  >
                    <option>延续当前</option>
                    <option>升高张力</option>
                    <option>降低张力</option>
                    <option>转向温情</option>
                    <option>转向激烈</option>
                    <option>转向悲凉</option>
                    <option>释放压力</option>
                  </select>
                </div>

                {/* Pace control */}
                <div>
                  <label className="block text-xs font-medium text-purple-500 mb-1">
                    节奏控制
                  </label>
                  <select
                    value={paceControl}
                    onChange={(e) => setPaceControl(e.target.value)}
                    className="w-full px-2 py-1 text-xs border rounded border-purple-300 dark:border-purple-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300"
                  >
                    <option>保持当前</option>
                    <option>加快节奏</option>
                    <option>放缓节奏</option>
                    <option>快节奏爽文</option>
                    <option>慢节奏细腻</option>
                  </select>
                </div>
              </div>
            )}

            {/* Intent input */}
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">创作意图</label>
              <textarea
                value={userIntent}
                onChange={(e) => setUserIntent(e.target.value)}
                placeholder='例如："这里要有压迫感""长老们开始质疑主角"'
                rows={3}
                className="w-full px-3 py-2 text-sm border rounded border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 resize-none"
              />
            </div>

            {/* Style note */}
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">风格偏好（可选）</label>
              <input
                type="text"
                value={styleNote}
                onChange={(e) => setStyleNote(e.target.value)}
                placeholder='例如："偏番茄风""古龙风格"'
                className="w-full px-3 py-1.5 text-sm border rounded border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              />
            </div>

            {/* Generate button */}
            <button
              onClick={handleContinue}
              disabled={generating}
              className="w-full py-2 px-4 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white rounded-md text-sm font-medium transition-colors"
            >
              {generating ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                  生成中...
                </span>
              ) : (
                "AI 续写"
              )}
            </button>

            {error && (
              <p className="text-sm text-red-500 p-2 bg-red-50 dark:bg-red-900/20 rounded">{error}</p>
            )}

            {/* AI Output */}
            {aiOutput && (
              <div className="space-y-3">
                <div className="border border-green-300 dark:border-green-700 bg-green-50 dark:bg-green-900/20 rounded-md p-3">
                  <h4 className="text-xs font-medium text-green-600 dark:text-green-400 mb-2">AI 续写结果</h4>
                  <div className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed max-h-80 overflow-y-auto">
                    {aiOutput}
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={handleAccept}
                    className="flex-1 py-1.5 px-3 bg-green-500 hover:bg-green-600 text-white rounded text-xs font-medium transition-colors"
                  >
                    接受并插入
                  </button>
                  <button
                    onClick={handleReject}
                    className="flex-1 py-1.5 px-3 bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-200 rounded text-xs font-medium transition-colors"
                  >
                    放弃
                  </button>
                </div>

                <button
                  onClick={handleRegenerate}
                  disabled={generating}
                  className="w-full py-1.5 px-3 border border-blue-300 dark:border-blue-700 text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded text-xs font-medium transition-colors disabled:opacity-50"
                >
                  重新生成
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </aside>
  );
}
