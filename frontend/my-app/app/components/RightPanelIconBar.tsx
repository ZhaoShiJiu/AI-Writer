"use client";

import type { ReactNode } from "react";

/* ──────────── SVG Icons (24×24, stroke-width 1.8) ──────────── */

function PlannerIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="3" width="16" height="18" rx="2" />
      <line x1="8" y1="8" x2="16" y2="8" />
      <line x1="8" y1="12" x2="16" y2="12" />
      <line x1="8" y1="16" x2="12" y2="16" />
    </svg>
  );
}

function StoryGraphIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="6" cy="6" r="2.5" />
      <circle cx="18" cy="6" r="2.5" />
      <circle cx="12" cy="18" r="2.5" />
      <line x1="8" y1="7.5" x2="10.5" y2="16" />
      <line x1="16" y1="7.5" x2="13.5" y2="16" />
      <line x1="7.5" y1="7.5" x2="16.5" y2="7.5" />
    </svg>
  );
}

function ForeshadowingIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="9" />
      <circle cx="12" cy="12" r="4" />
      <line x1="12" y1="2" x2="12" y2="6" />
      <line x1="12" y1="18" x2="12" y2="22" />
      <line x1="2" y1="12" x2="6" y2="12" />
      <line x1="18" y1="12" x2="22" y2="12" />
    </svg>
  );
}

function TimelineIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <line x1="4" y1="4" x2="4" y2="20" />
      <circle cx="4" cy="6" r="2" fill="currentColor" />
      <line x1="10" y1="6" x2="20" y2="6" />
      <circle cx="4" cy="14" r="2" />
      <line x1="10" y1="14" x2="20" y2="14" />
      <circle cx="4" cy="20" r="1.5" fill="currentColor" />
    </svg>
  );
}

function StyleIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2l2.5 6.5L21 9l-5 4.5L17.5 21 12 17l-5.5 4L8 13.5 3 9l6.5-.5z" />
    </svg>
  );
}

function NarrativeIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="14" width="4" height="6" rx="0.5" />
      <rect x="10" y="8" width="4" height="12" rx="0.5" />
      <rect x="17" y="4" width="4" height="16" rx="0.5" />
    </svg>
  );
}

function MemoryIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2a3 3 0 0 0-2.5 1.3A3 3 0 0 0 7 4.5C7 7 9 9 12 12c3-3 5-5 5-7.5a3 3 0 0 0-5-2.7A3 3 0 0 0 12 2z" />
      <path d="M6 16c-1.5 1-3 2.5-3 4.5 0 1 .8 1.5 1.5 1.5h15c.7 0 1.5-.5 1.5-1.5 0-2-1.5-3.5-3-4.5" />
      <circle cx="12" cy="11" r="1.5" fill="currentColor" />
    </svg>
  );
}

function AIIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2l1.5 5.5L19 8l-4 3.5L16.5 18 12 14.5 7.5 18 9 11.5 5 8l5.5-.5z" />
      <circle cx="12" cy="11" r="1.5" fill="currentColor" />
    </svg>
  );
}

function HistoryIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="9" />
      <polyline points="12,6 12,12 16,14" />
    </svg>
  );
}

/* ──────────── Panel definitions ──────────── */

interface PanelDef {
  id: string;
  label: string;
  desc: string;
  icon: ReactNode;
}

const PANELS: PanelDef[] = [
  {
    id: "planner",
    label: "写作规划",
    desc: "AI分析并生成写作规划方案",
    icon: <PlannerIcon />,
  },
  {
    id: "storygraph",
    label: "故事图谱",
    desc: "人物、事件、势力关系网络",
    icon: <StoryGraphIcon />,
  },
  {
    id: "foreshadowing",
    label: "伏笔管理",
    desc: "伏笔埋设、提醒与回收追踪",
    icon: <ForeshadowingIcon />,
  },
  {
    id: "timeline",
    label: "叙事时间线",
    desc: "主线、支线、角色线时间轴",
    icon: <TimelineIcon />,
  },
  {
    id: "style",
    label: "风格分析",
    desc: "AI分析并维护写作风格画像",
    icon: <StyleIcon />,
  },
  {
    id: "narrative",
    label: "叙事分析",
    desc: "节奏、情绪、张力叙事状态",
    icon: <NarrativeIcon />,
  },
  {
    id: "memory",
    label: "记忆管理",
    desc: "角色状态与世界设定记忆",
    icon: <MemoryIcon />,
  },
  {
    id: "ai",
    label: "AI写作",
    desc: "AI续写、改写与润色辅助",
    icon: <AIIcon />,
  },
  {
    id: "history",
    label: "生成历史",
    desc: "查看历史AI生成记录",
    icon: <HistoryIcon />,
  },
];

/* ──────────── Component ──────────── */

export default function RightPanelIconBar() {
  return (
    <div className="flex flex-col items-center py-3 gap-1 w-full h-full bg-gray-50/80 dark:bg-gray-900/80 border-l border-gray-200 dark:border-gray-700 select-none">
      {PANELS.map((panel) => (
        <div key={panel.id} className="w-full flex justify-center">
          <div className="group relative">
            {/* Tooltip — positioned to the left of the icon */}
            <div
              className="
                absolute right-full mr-2 top-1/2 -translate-y-1/2
                px-3 py-2 bg-gray-800 dark:bg-gray-700
                text-white rounded-md shadow-lg
                opacity-0 pointer-events-none
                group-hover:opacity-100
                transition-opacity duration-100
                z-50 whitespace-nowrap
              "
            >
              <div className="text-xs font-semibold">{panel.label}</div>
              <div className="text-[10px] text-gray-300 dark:text-gray-400 mt-0.5">
                {panel.desc}
              </div>
              {/* Arrow pointing right */}
              <div className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-full">
                <div className="w-0 h-0 border-t-[5px] border-t-transparent border-b-[5px] border-b-transparent border-l-[5px] border-l-gray-800 dark:border-l-gray-700" />
              </div>
            </div>

            {/* Icon button */}
            <div
              className="
                p-2 rounded-lg cursor-default
                hover:bg-gray-200 dark:hover:bg-gray-700
                transition-colors
                text-gray-400 dark:text-gray-500
                hover:text-gray-700 dark:hover:text-gray-200
              "
              title={panel.label}
            >
              {panel.icon}
            </div>
          </div>
        </div>
      ))}

      {/* Bottom hint */}
      <div className="mt-auto pb-2">
        <span
          className="text-[9px] text-gray-300 dark:text-gray-600"
          style={{ writingMode: "vertical-rl" }}
        >
          悬停查看功能
        </span>
      </div>
    </div>
  );
}
