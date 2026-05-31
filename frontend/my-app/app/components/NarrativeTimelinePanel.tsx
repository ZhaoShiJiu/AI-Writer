"use client";
import { useEffect, useState } from "react";
import { useNovelStore } from "@/app/store/useNovelStore";
import * as api from "@/app/lib/api";
import type { StoryArc } from "@/app/types";

const ARC_STATUS_COLORS: Record<string, string> = {
  planned: "bg-gray-200 dark:bg-gray-600",
  active: "bg-blue-400 dark:bg-blue-600",
  completed: "bg-green-400 dark:bg-green-600",
};

const ARC_TYPE_LABELS: Record<string, string> = {
  main: "主线",
  sub: "支线",
  character: "角色线",
};

export default function NarrativeTimelinePanel() {
  const { currentNovelId, narrativeStates } = useNovelStore();
  const [arcs, setArcs] = useState<StoryArc[]>([]);
  const [expanded, setExpanded] = useState(false);

  const loadData = async () => {
    if (!currentNovelId) return;
    try {
      const result = await api.listStoryArcs(currentNovelId);
      setArcs(result.arcs);
    } catch { /* ignore */ }
  };

  useEffect(() => {
    if (currentNovelId && expanded) { loadData(); }
    else { setArcs([]); }
  }, [currentNovelId, expanded]);

  if (!currentNovelId) {
    return (
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-sm font-semibold text-teal-600 dark:text-teal-400 uppercase tracking-wider">V4 叙事时间线</h2>
        <p className="text-xs text-gray-400 mt-2">请先选择小说</p>
      </div>
    );
  }

  const hasData = arcs.length > 0 || narrativeStates.length > 0;

  return (
    <div className="border-b border-gray-200 dark:border-gray-700">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800/50"
      >
        <h2 className="text-sm font-semibold text-teal-600 dark:text-teal-400 uppercase tracking-wider">V4 叙事时间线</h2>
        <span className="text-xs text-gray-400">{expanded ? "收起" : "展开"}</span>
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-3 max-h-96 overflow-y-auto">
          {!hasData && (
            <p className="text-xs text-gray-400">暂无时间线数据，创建故事线或分析章节后显示</p>
          )}

          {/* Story arcs */}
          {arcs.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs font-medium text-teal-600 dark:text-teal-400">📖 故事线</div>
              {arcs.map(arc => (
                <div key={arc.id} className="p-2 bg-gray-50 dark:bg-gray-800 rounded text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-700 dark:text-gray-300">{arc.title}</span>
                    <span className="text-[10px] text-gray-400">[{ARC_TYPE_LABELS[arc.arc_type] || arc.arc_type}]</span>
                    <span className={`ml-auto w-2 h-2 rounded-full ${ARC_STATUS_COLORS[arc.status] || "bg-gray-300"}`} />
                  </div>
                  {arc.description && (
                    <div className="text-gray-500 mt-0.5 line-clamp-2">{arc.description}</div>
                  )}
                  {/* Mini progress bar */}
                  {(arc.start_chapter_id || arc.end_chapter_id) && (
                    <div className="mt-1.5 h-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${arc.status === "completed" ? "bg-green-400" : "bg-blue-400"}`}
                        style={{ width: arc.status === "completed" ? "100%" : arc.status === "active" ? "50%" : "10%" }}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Narrative states summary */}
          {narrativeStates.length > 0 && (
            <div className="space-y-1.5">
              <div className="text-xs font-medium text-teal-600 dark:text-teal-400">📊 情绪曲线</div>
              <div className="flex items-end gap-1 h-12">
                {narrativeStates.slice(-20).map((ns, i) => {
                  const height = Math.max(4, (ns.tension_score / 10) * 48);
                  const colors: Record<string, string> = {
                    "紧张": "bg-red-400", "热血": "bg-orange-400", "悲凉": "bg-blue-400",
                    "温情": "bg-amber-400", "压抑": "bg-gray-500", "恐惧": "bg-purple-500",
                  };
                  return (
                    <div
                      key={i}
                      className={`flex-1 rounded-t ${colors[ns.emotion || ""] || "bg-teal-400"}`}
                      style={{ height: `${height}px` }}
                      title={`Ch${ns.chapter_id}: ${ns.emotion} ${ns.tension_score}`}
                    />
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
