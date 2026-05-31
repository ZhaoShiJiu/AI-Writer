"use client";
import { useEffect, useState } from "react";
import { useNovelStore } from "@/app/store/useNovelStore";
import * as api from "@/app/lib/api";
import type { CharacterMemory, WorldMemory } from "@/app/types";

export default function MemoryPanel() {
  const { currentNovelId, currentChapter } = useNovelStore();
  const [characters, setCharacters] = useState<CharacterMemory[]>([]);
  const [world, setWorld] = useState<WorldMemory | null>(null);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(true);

  const loadMemory = async () => {
    if (!currentNovelId) return;
    setLoading(true);
    try {
      const snapshot = await api.getMemorySnapshot(currentNovelId);
      setCharacters(snapshot.characters);
      setWorld(snapshot.world);
    } catch {
      // silently fail
    }
    setLoading(false);
  };

  useEffect(() => {
    if (currentNovelId) {
      loadMemory();
    } else {
      setCharacters([]);
      setWorld(null);
    }
  }, [currentNovelId]);

  const handleUpdateMemory = async () => {
    if (!currentChapter) return;
    try {
      await api.updateChapterMemory(currentChapter.id);
      await loadMemory();
    } catch {
      // silently fail
    }
  };

  if (!currentNovelId) {
    return (
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">V2 记忆系统</h2>
        <p className="text-xs text-gray-400 mt-2">请先选择小说</p>
      </div>
    );
  }

  return (
    <div className="border-b border-gray-200 dark:border-gray-700">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800/50"
      >
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">V2 记忆系统</h2>
        <span className="text-xs text-gray-400">{expanded ? "收起" : "展开"}</span>
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-4 max-h-96 overflow-y-auto">
          {loading && (
            <p className="text-xs text-gray-400">加载记忆中...</p>
          )}
          {/* Characters */}
          <div>
            <h3 className="text-xs font-medium text-gray-500 mb-2">角色记忆</h3>
            {characters.length === 0 ? (

            <p className="text-xs text-gray-400">暂无角色记忆，保存章节后可自动生成</p>
            ) : (
              <div className="space-y-2">
                {characters.map((char) => (
                  <div key={char.id} className="p-2 bg-gray-50 dark:bg-gray-800 rounded text-xs">
                    <div className="font-medium text-gray-700 dark:text-gray-300">{char.character_name}</div>
                    {char.memory_json.realm && <div className="text-gray-500 mt-0.5">境界：{char.memory_json.realm}</div>}
                    {char.memory_json.personality && char.memory_json.personality.length > 0 && <div className="text-gray-500 mt-0.5">性格：{char.memory_json.personality.join("、")}</div>}
                    {char.memory_json.notes && <div className="text-gray-400 mt-0.5">{char.memory_json.notes}</div>}
                  </div>
                ))}
              </div>
            )}
          </div>
          {/* World Memory */}
          <div>
            <h3 className="text-xs font-medium text-gray-500 mb-2">世界观记忆</h3>
            {(!world || !world.world_state || Object.keys(world.world_state).length === 0) &&
              !world?.world_state?.notes ? (
              <p className="text-xs text-gray-400">暂无世界观记忆</p>
            ) : (
              <div className="space-y-3">
                {/* 主要势力 */}
                {world.world_state.major_factions && world.world_state.major_factions.length > 0 && (
                  <div>
                    <div className="text-xs font-medium text-amber-600 dark:text-amber-400 mb-1.5">
                      🏛 主要势力
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {world.world_state.major_factions.map((f, i) => (
                        <span key={i} className="px-2 py-0.5 text-xs bg-amber-50 dark:bg-amber-900/30 text-amber-800 dark:text-amber-200 rounded-full border border-amber-200 dark:border-amber-700">
                          {f}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* 世界规则 */}
                {world.world_state.world_rules && world.world_state.world_rules.length > 0 && (
                  <div>
                    <div className="text-xs font-medium text-blue-600 dark:text-blue-400 mb-1.5">
                      📜 世界规则
                    </div>
                    <ul className="space-y-1">
                      {world.world_state.world_rules.map((r, i) => (
                        <li key={i} className="flex items-start gap-1.5 text-xs text-gray-600 dark:text-gray-400">
                          <span className="text-blue-400 mt-0.5 shrink-0">•</span>
                          <span>{r}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* 当前冲突 */}
                {world.world_state.current_conflicts && world.world_state.current_conflicts.length > 0 && (
                  <div>
                    <div className="text-xs font-medium text-red-600 dark:text-red-400 mb-1.5">
                      ⚔ 当前冲突
                    </div>
                    <ul className="space-y-1">
                      {world.world_state.current_conflicts.map((c, i) => (
                        <li key={i} className="flex items-start gap-1.5 text-xs text-gray-600 dark:text-gray-400">
                          <span className="text-red-400 mt-0.5 shrink-0">▸</span>
                          <span>{c}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* 地点 */}
                {world.world_state.locations && world.world_state.locations.length > 0 && (
                  <div>
                    <div className="text-xs font-medium text-green-600 dark:text-green-400 mb-1.5">
                      📍 重要地点
                    </div>
                    <div className="space-y-1.5">
                      {world.world_state.locations.map((loc, i) => (
                        <div key={i} className="p-2 bg-green-50 dark:bg-green-900/20 rounded text-xs border border-green-100 dark:border-green-800">
                          <span className="font-medium text-green-700 dark:text-green-300">{loc.name}</span>
                          {loc.description && (
                            <span className="text-gray-500 dark:text-gray-400 ml-1.5">{loc.description}</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 备注 */}
                {world.world_state.notes && (
                  <div>
                    <div className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                      📝 备注
                    </div>
                    <p className="text-xs text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-2 rounded leading-relaxed">
                      {world.world_state.notes}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
          {currentChapter && (
            <button onClick={handleUpdateMemory} disabled={loading} className="w-full py-1.5 px-3 bg-purple-500 hover:bg-purple-600 disabled:bg-purple-300 text-white rounded text-xs font-medium transition-colors">
              {loading ? "分析中..." : "更新记忆"}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
