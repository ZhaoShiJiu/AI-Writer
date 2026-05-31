"use client";
import { useEffect, useState } from "react";
import { useNovelStore } from "@/app/store/useNovelStore";
import * as api from "@/app/lib/api";
import type { Foreshadowing } from "@/app/types";

const STATUS_COLORS: Record<string, string> = {
  planned: "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400",
  planted: "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300",
  reminded: "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300",
  payoff: "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300",
};

const STATUS_LABELS: Record<string, string> = {
  planned: "规划中",
  planted: "已埋设",
  reminded: "已提醒",
  payoff: "已回收",
};

export default function ForeshadowingPanel() {
  const { currentNovelId, currentChapter } = useNovelStore();
  const [foreshadowings, setForeshadowings] = useState<Foreshadowing[]>([]);
  const [expanded, setExpanded] = useState(true);
  const [newName, setNewName] = useState("");
  const [newDesc, setNewDesc] = useState("");

  const loadData = async () => {
    if (!currentNovelId) return;
    try {
      const result = await api.listForeshadowings(currentNovelId);
      setForeshadowings(result.foreshadowings);
    } catch { /* ignore */ }
  };

  useEffect(() => {
    if (currentNovelId) { loadData(); }
    else { setForeshadowings([]); }
  }, [currentNovelId]);

  const handlePayoff = async (id: number) => {
    if (!currentChapter) return;
    try {
      await api.updateForeshadowing(id, { status: "payoff", payoff_at_chapter_id: currentChapter.id });
      await loadData();
    } catch { /* ignore */ }
  };

  const handleRemind = async (id: number) => {
    try {
      await api.updateForeshadowing(id, { status: "reminded" });
      await loadData();
    } catch { /* ignore */ }
  };

  const handleCreate = async () => {
    if (!currentNovelId || !newName.trim()) return;
    try {
      await api.createForeshadowing(currentNovelId, {
        name: newName.trim(),
        description: newDesc.trim(),
        status: "planted",
      });
      setNewName("");
      setNewDesc("");
      await loadData();
    } catch { /* ignore */ }
  };

  if (!currentNovelId) {
    return (
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-sm font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-wider">V4 伏笔管理</h2>
        <p className="text-xs text-gray-400 mt-2">请先选择小说</p>
      </div>
    );
  }

  const pending = foreshadowings.filter(f => f.status !== "payoff");
  const paid = foreshadowings.filter(f => f.status === "payoff");

  return (
    <div className="border-b border-gray-200 dark:border-gray-700">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800/50"
      >
        <h2 className="text-sm font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-wider">
          V4 伏笔管理 {pending.length > 0 && `(${pending.length})`}
        </h2>
        <span className="text-xs text-gray-400">{expanded ? "收起" : "展开"}</span>
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-3 max-h-96 overflow-y-auto">
          {/* Pending foreshadowings */}
          {pending.length > 0 && (
            <div className="space-y-1.5">
              <div className="text-xs font-medium text-amber-600 dark:text-amber-400">
                ⚠ 待回收 ({pending.length})
              </div>
              {pending.map(f => (
                <div key={f.id} className="p-2 bg-amber-50 dark:bg-amber-900/20 rounded text-xs border border-amber-100 dark:border-amber-800">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="font-medium text-gray-700 dark:text-gray-300">{f.name}</div>
                      {f.description && <div className="text-gray-500 mt-0.5">{f.description}</div>}
                      <span className={`inline-block mt-1 px-1.5 py-0.5 rounded text-[10px] ${STATUS_COLORS[f.status]}`}>
                        {STATUS_LABELS[f.status]}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-1 mt-1.5">
                    <button
                      onClick={() => handleRemind(f.id)}
                      className="px-2 py-0.5 bg-blue-100 hover:bg-blue-200 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 text-blue-600 dark:text-blue-400 rounded text-[10px]"
                    >
                      提醒
                    </button>
                    {currentChapter && (
                      <button
                        onClick={() => handlePayoff(f.id)}
                        className="px-2 py-0.5 bg-green-100 hover:bg-green-200 dark:bg-green-900/30 dark:hover:bg-green-900/50 text-green-600 dark:text-green-400 rounded text-[10px]"
                      >
                        标记回收
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Paid off */}
          {paid.length > 0 && (
            <div className="space-y-1">
              <div className="text-xs font-medium text-green-600 dark:text-green-400">
                ✓ 已回收 ({paid.length})
              </div>
              {paid.slice(0, 3).map(f => (
                <div key={f.id} className="text-xs text-gray-400 truncate">{f.name}</div>
              ))}
            </div>
          )}

          {/* Add new */}
          <div className="space-y-1.5 pt-2 border-t border-gray-100 dark:border-gray-700">
            <input
              type="text"
              value={newName}
              onChange={e => setNewName(e.target.value)}
              placeholder="伏笔名称..."
              className="w-full px-2 py-1 text-xs border rounded border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            />
            <input
              type="text"
              value={newDesc}
              onChange={e => setNewDesc(e.target.value)}
              placeholder="伏笔描述..."
              className="w-full px-2 py-1 text-xs border rounded border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            />
            <button
              onClick={handleCreate}
              className="w-full py-1 px-3 bg-amber-500 hover:bg-amber-600 text-white rounded text-xs font-medium transition-colors"
            >
              + 手动添加伏笔
            </button>
          </div>

          {foreshadowings.length === 0 && (
            <p className="text-xs text-gray-400">暂无伏笔数据，保存章节后AI会自动检测，或手动添加</p>
          )}
        </div>
      )}
    </div>
  );
}
