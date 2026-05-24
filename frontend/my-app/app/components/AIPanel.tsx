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
    clearAiOutput,
    saveChapter,
    acceptGeneration,
    error,
  } = useNovelStore();

  const [userIntent, setUserIntent] = useState("");
  const [styleNote, setStyleNote] = useState("");

  const handleContinue = async () => {
    if (!currentChapter) return;
    await continueWriting(userIntent, styleNote);
  };

  const handleRegenerate = async () => {
    if (!currentChapter) return;
    await regenerateWriting(userIntent, styleNote);
  };

  const handleAccept = async () => {
    if (!currentChapter || !aiOutput) return;

    // Append AI output to chapter content
    const currentContent = currentChapter.content || "";
    const newContent = currentContent + "\n\n" + aiOutput;
    await saveChapter(newContent);

    // Mark generation as accepted
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

  return (
    <aside className="flex-1 overflow-hidden flex flex-col">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">AI 协同创作</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {!currentChapter ? (
          <p className="text-sm text-gray-400">请先选择要续写的章节</p>
        ) : (
          <>
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
