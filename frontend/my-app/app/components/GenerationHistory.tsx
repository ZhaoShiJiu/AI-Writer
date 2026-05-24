"use client";

import { useNovelStore } from "@/app/store/useNovelStore";

export default function GenerationHistory() {
  const { generations, currentChapter } = useNovelStore();

  if (!currentChapter) return null;
  if (generations.length === 0) return null;

  return (
    <div className="border-t border-gray-200 dark:border-gray-700">
      <div className="p-3">
        <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">生成历史</h3>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {generations.slice(0, 10).map((gen) => (
            <div
              key={gen.id}
              className={`p-2 rounded text-xs ${
                gen.accepted
                  ? "bg-green-50 dark:bg-green-900/10 border border-green-200 dark:border-green-800"
                  : "bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-gray-400">
                  {new Date(gen.created_at).toLocaleTimeString("zh-CN", {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
                {gen.accepted && (
                  <span className="text-green-500 text-xs">已采纳</span>
                )}
              </div>
              {gen.user_intent && (
                <p className="text-gray-500 dark:text-gray-400 mb-1">意图: {gen.user_intent}</p>
              )}
              <p className="text-gray-600 dark:text-gray-300 line-clamp-3 whitespace-pre-wrap">
                {gen.ai_output}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
