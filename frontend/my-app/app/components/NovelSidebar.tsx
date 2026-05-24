"use client";

import { useState } from "react";
import { useNovelStore } from "@/app/store/useNovelStore";

export default function NovelSidebar() {
  const {
    novels,
    chapters,
    currentNovelId,
    currentChapterId,
    loadNovels,
    createNovel,
    selectNovel,
    deleteNovel,
    createChapter,
    selectChapter,
    deleteChapter,
    loading,
  } = useNovelStore();

  const [newTitle, setNewTitle] = useState("");
  const [showCreateNovel, setShowCreateNovel] = useState(false);

  const handleCreateNovel = async () => {
    if (!newTitle.trim()) return;
    const novel = await createNovel(newTitle.trim());
    if (novel) {
      setNewTitle("");
      setShowCreateNovel(false);
      selectNovel(novel.id);
    }
  };

  const handleCreateChapter = async () => {
    if (!currentNovelId) return;
    const chapter = await createChapter(currentNovelId);
    if (chapter) {
      selectChapter(chapter.id);
    }
  };

  return (
    <aside className="w-64 h-full border-r border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 flex flex-col">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">我的小说</h2>
      </div>

      {/* Novel list */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {novels.map((novel) => (
          <div key={novel.id}>
            <button
              onClick={() => selectNovel(novel.id)}
              className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors flex items-center justify-between group ${
                currentNovelId === novel.id
                  ? "bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200"
                  : "hover:bg-gray-200 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300"
              }`}
            >
              <span className="truncate">{novel.title}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  if (confirm("确定删除这本小说吗？")) deleteNovel(novel.id);
                }}
                className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-600 text-xs px-1"
              >
                ✕
              </button>
            </button>

            {/* Chapter list under selected novel */}
            {currentNovelId === novel.id && (
              <div className="ml-3 mt-1 space-y-0.5">
                {chapters.map((ch) => (
                  <button
                    key={ch.id}
                    onClick={() => selectChapter(ch.id)}
                    className={`w-full text-left px-3 py-1.5 rounded text-xs transition-colors flex items-center justify-between group ${
                      currentChapterId === ch.id
                        ? "bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-200"
                        : "hover:bg-gray-200 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-400"
                    }`}
                  >
                    <span className="truncate">{ch.title}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm("确定删除这个章节吗？")) deleteChapter(ch.id);
                      }}
                      className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-600 text-xs px-1"
                    >
                      ✕
                    </button>
                  </button>
                ))}
                <button
                  onClick={handleCreateChapter}
                  className="w-full text-left px-3 py-1.5 rounded text-xs text-blue-500 hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
                >
                  + 新建章节
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Create novel */}
      <div className="p-3 border-t border-gray-200 dark:border-gray-700">
        {showCreateNovel ? (
          <div className="space-y-2">
            <input
              type="text"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="小说标题..."
              className="w-full px-2 py-1.5 text-sm border rounded border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              onKeyDown={(e) => e.key === "Enter" && handleCreateNovel()}
            />
            <div className="flex gap-1">
              <button
                onClick={handleCreateNovel}
                className="flex-1 px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                创建
              </button>
              <button
                onClick={() => setShowCreateNovel(false)}
                className="px-2 py-1 text-xs bg-gray-300 dark:bg-gray-600 rounded hover:bg-gray-400"
              >
                取消
              </button>
            </div>
          </div>
        ) : (
          <button
            onClick={() => setShowCreateNovel(true)}
            className="w-full px-3 py-2 text-sm text-blue-500 hover:bg-gray-200 dark:hover:bg-gray-800 rounded-md transition-colors"
          >
            + 新建小说
          </button>
        )}
      </div>
    </aside>
  );
}
