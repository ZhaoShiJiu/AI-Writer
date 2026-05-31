"use client";
import { useEffect, useState } from "react";
import { useNovelStore } from "@/app/store/useNovelStore";
import * as api from "@/app/lib/api";
import type { StoryGraphData, StoryGraphNode, StoryGraphEdge } from "@/app/types";

const NODE_COLORS: Record<string, string> = {
  character: "bg-blue-100 dark:bg-blue-900/50 border-blue-400 dark:border-blue-500",
  event: "bg-green-100 dark:bg-green-900/50 border-green-400 dark:border-green-500",
  faction: "bg-orange-100 dark:bg-orange-900/50 border-orange-400 dark:border-orange-500",
  location: "bg-purple-100 dark:bg-purple-900/50 border-purple-400 dark:border-purple-500",
};

const NODE_LABEL_COLORS: Record<string, string> = {
  character: "text-blue-700 dark:text-blue-300",
  event: "text-green-700 dark:text-green-300",
  faction: "text-orange-700 dark:text-orange-300",
  location: "text-purple-700 dark:text-purple-300",
};

export default function StoryGraphPanel() {
  const { currentNovelId } = useNovelStore();
  const [graphData, setGraphData] = useState<StoryGraphData | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    if (!currentNovelId) return;
    setLoading(true);
    try {
      const data = await api.getStoryGraph(currentNovelId);
      if (data.nodes.length > 0) setGraphData(data);
    } catch { /* ignore */ }
    setLoading(false);
  };

  useEffect(() => {
    if (currentNovelId && expanded) { loadData(); }
    else { setGraphData(null); }
  }, [currentNovelId, expanded]);

  const getConnectedEdges = (nodeId: string): StoryGraphEdge[] => {
    if (!graphData) return [];
    return graphData.edges.filter(e => e.source === nodeId || e.target === nodeId);
  };

  const getNodeById = (id: string): StoryGraphNode | undefined => {
    return graphData?.nodes.find(n => n.id === id);
  };

  if (!currentNovelId) {
    return (
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-sm font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-wider">V4 故事图谱</h2>
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
        <h2 className="text-sm font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-wider">V4 故事图谱</h2>
        <span className="text-xs text-gray-400">{expanded ? "收起" : "展开"}</span>
      </button>

      {expanded && (
        <div className="px-4 pb-4 max-h-96 overflow-y-auto">
          {loading && <p className="text-xs text-gray-400">加载图谱中...</p>}

          {!loading && (!graphData || graphData.nodes.length === 0) && (
            <p className="text-xs text-gray-400">
              {graphData ? "暂无图谱数据，保存章节后将自动构建" : "Neo4j 未启用或暂无数据"}
            </p>
          )}

          {graphData && graphData.nodes.length > 0 && (
            <div className="space-y-3">
              {/* Stats */}
              <div className="flex gap-2 text-[10px] text-gray-500">
                <span className={NODE_LABEL_COLORS.character}>角色 {graphData.nodes.filter(n => n.node_type === "character").length}</span>
                <span className={NODE_LABEL_COLORS.event}>事件 {graphData.nodes.filter(n => n.node_type === "event").length}</span>
                <span className={NODE_LABEL_COLORS.faction}>势力 {graphData.nodes.filter(n => n.node_type === "faction").length}</span>
              </div>

              {/* Node list */}
              <div className="space-y-1">
                {graphData.nodes.map(node => {
                  const isSelected = selectedNode === node.id;
                  const connectedEdges = isSelected ? getConnectedEdges(node.id) : [];
                  return (
                    <div key={node.id}>
                      <button
                        onClick={() => setSelectedNode(isSelected ? null : node.id)}
                        className={`w-full text-left px-2 py-1.5 rounded text-xs border transition-colors ${NODE_COLORS[node.node_type] || "border-gray-300"} ${isSelected ? "ring-1 ring-blue-400" : ""}`}
                      >
                        <span className="font-medium">{node.label}</span>
                        {node.node_type === "character" && Boolean(node.properties?.realm) && (
                          <span className="text-gray-400 ml-1">({String(node.properties.realm)})</span>
                        )}
                      </button>
                      {/* Connected edges when selected */}
                      {isSelected && connectedEdges.length > 0 && (
                        <div className="ml-3 mt-0.5 space-y-0.5">
                          {connectedEdges.map((edge, i) => {
                            const otherId = edge.source === node.id ? edge.target : edge.source;
                            const otherNode = getNodeById(otherId);
                            return (
                              <div key={i} className="text-[10px] text-gray-500 flex items-center gap-1">
                                <span className="text-gray-400">{edge.source === node.id ? "→" : "←"}</span>
                                <span className={otherNode ? NODE_LABEL_COLORS[otherNode.node_type] : ""}>
                                  {otherNode?.label || otherId}
                                </span>
                                <span className="text-gray-400">({edge.edge_type})</span>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
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
