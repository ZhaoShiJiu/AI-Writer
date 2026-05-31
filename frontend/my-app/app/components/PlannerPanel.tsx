"use client";
import { useEffect, useState } from "react";
import { useNovelStore } from "@/app/store/useNovelStore";
import * as api from "@/app/lib/api";
import type { PlanAnalysisResult, PlanData, WritingPlan } from "@/app/types";

export default function PlannerPanel() {
  const { currentNovelId } = useNovelStore();
  const [expanded, setExpanded] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<PlanAnalysisResult | null>(null);
  const [plans, setPlans] = useState<WritingPlan[]>([]);
  const [genre, setGenre] = useState("");
  const [theme, setTheme] = useState("");
  const [plotDirection, setPlotDirection] = useState("");

  const loadData = async () => {
    if (!currentNovelId) return;
    try {
      const result = await api.getWritingPlans(currentNovelId);
      setPlans(result.plans);
    } catch { /* ignore */ }
  };

  useEffect(() => {
    if (currentNovelId) { loadData(); }
    else { setAnalysis(null); setPlans([]); }
  }, [currentNovelId]);

  const handleAutoAnalyze = async () => {
    if (!currentNovelId) return;
    setAnalyzing(true);
    try {
      const result = await api.autoAnalyzeNovel(currentNovelId);
      setAnalysis(result);
      setGenre(result.genre || "");
      setTheme(result.themes?.join("、") || "");
    } catch { /* ignore */ }
    setAnalyzing(false);
  };

  const handleCreatePlan = async () => {
    if (!currentNovelId) return;
    const planData: PlanData = {
      genre: genre || analysis?.genre || "",
      themes: theme ? theme.split(/[、,]/).map(s => s.trim()) : (analysis?.themes || []),
      scene_plan: [],
      theme_notes: plotDirection,
    };
    try {
      await api.createWritingPlan(currentNovelId, {
        plan_type: "chapter",
        manual_genre: genre,
        manual_theme: theme,
        manual_plot_direction: plotDirection,
        plan_data: planData,
      });
      await loadData();
    } catch { /* ignore */ }
  };

  if (!currentNovelId) {
    return (
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-sm font-semibold text-purple-600 dark:text-purple-400 uppercase tracking-wider">V4 叙事规划</h2>
        <p className="text-xs text-gray-400 mt-2">请先选择小说</p>
      </div>
    );
  }

  const latestPlan = plans[0];

  return (
    <div className="border-b border-gray-200 dark:border-gray-700">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800/50"
      >
        <h2 className="text-sm font-semibold text-purple-600 dark:text-purple-400 uppercase tracking-wider">V4 叙事规划</h2>
        <span className="text-xs text-gray-400">{expanded ? "收起" : "展开"}</span>
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-3 max-h-96 overflow-y-auto">
          {/* Auto-analyze button */}
          <button
            onClick={handleAutoAnalyze}
            disabled={analyzing}
            className="w-full py-1.5 px-3 bg-purple-500 hover:bg-purple-600 disabled:bg-purple-300 text-white rounded text-xs font-medium transition-colors"
          >
            {analyzing ? "分析中..." : "🤖 自动分析小说"}
          </button>

          {/* Analysis result */}
          {analysis && (
            <div className="p-2 bg-purple-50 dark:bg-purple-900/20 rounded text-xs space-y-1">
              <div><span className="text-purple-600 dark:text-purple-400 font-medium">类型：</span>{analysis.genre}</div>
              <div><span className="text-purple-600 dark:text-purple-400 font-medium">主题：</span>{analysis.themes?.join("、")}</div>
              <div><span className="text-purple-600 dark:text-purple-400 font-medium">角色：</span>{analysis.main_characters?.join("、")}</div>
              <div><span className="text-purple-600 dark:text-purple-400 font-medium">结构：</span>{analysis.narrative_structure}</div>
            </div>
          )}

          {/* Manual inputs */}
          <div className="space-y-2">
            <input
              type="text"
              value={genre}
              onChange={e => setGenre(e.target.value)}
              placeholder="小说类型（如：玄幻、都市）"
              className="w-full px-2 py-1 text-xs border rounded border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            />
            <input
              type="text"
              value={theme}
              onChange={e => setTheme(e.target.value)}
              placeholder="主题（如：成长与宿命）"
              className="w-full px-2 py-1 text-xs border rounded border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            />
            <textarea
              value={plotDirection}
              onChange={e => setPlotDirection(e.target.value)}
              placeholder="剧情方向描述..."
              rows={2}
              className="w-full px-2 py-1 text-xs border rounded border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            />
            <button
              onClick={handleCreatePlan}
              className="w-full py-1.5 px-3 bg-blue-500 hover:bg-blue-600 text-white rounded text-xs font-medium transition-colors"
            >
              更新规划
            </button>
          </div>

          {/* Latest plan */}
          {latestPlan && (
            <div className="space-y-2">
              <div className="text-xs font-medium text-gray-500">最新计划</div>
              <div className="p-2 bg-gray-50 dark:bg-gray-800 rounded text-xs">
                <div className="text-gray-600 dark:text-gray-400">
                  类型：{latestPlan.plan_json?.genre || "未指定"}
                </div>
                {latestPlan.plan_json?.scene_plan && Array.isArray(latestPlan.plan_json.scene_plan) && latestPlan.plan_json.scene_plan.length > 0 && (
                  <div className="mt-1 text-gray-500">
                    {latestPlan.plan_json.scene_plan.length} 个场景已规划
                  </div>
                )}
              </div>
            </div>
          )}

          {!analysis && plans.length === 0 && (
            <p className="text-xs text-gray-400">点击上方按钮自动分析小说，或手动填写类型和主题</p>
          )}
        </div>
      )}
    </div>
  );
}
