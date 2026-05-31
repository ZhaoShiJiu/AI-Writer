"use client";

import { useEffect, useState } from "react";
import { useNovelStore } from "@/app/store/useNovelStore";
import NovelSidebar from "@/app/components/NovelSidebar";
import Editor from "@/app/components/Editor";
import AIPanel from "@/app/components/AIPanel";
import GenerationHistory from "@/app/components/GenerationHistory";
import MemoryPanel from "@/app/components/MemoryPanel";
import StylePanel from "@/app/components/StylePanel";
import NarrativePanel from "@/app/components/NarrativePanel";
import PlannerPanel from "@/app/components/PlannerPanel";
import ForeshadowingPanel from "@/app/components/ForeshadowingPanel";
import StoryGraphPanel from "@/app/components/StoryGraphPanel";
import NarrativeTimelinePanel from "@/app/components/NarrativeTimelinePanel";
import RightPanelIconBar from "@/app/components/RightPanelIconBar";

function RightToggleBtn({
  visible,
  onClick,
}: {
  visible: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={
        "flex-shrink-0 flex items-center justify-center bg-gray-100 dark:bg-gray-800 " +
        "hover:bg-gray-200 dark:hover:bg-gray-700 border-gray-200 dark:border-gray-700 " +
        "transition-colors group z-10 h-full " +
        "border-l w-5 rounded-l-md"
      }
      title={visible ? "隐藏面板" : "显示面板"}
    >
      <span className="text-[10px] text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300 leading-none">
        {visible ? "▶" : "◀"}
      </span>
    </button>
  );
}

export default function Home() {
  const loadNovels = useNovelStore((s) => s.loadNovels);
  const [showLeft, setShowLeft] = useState(true);
  const [showRight, setShowRight] = useState(true);

  useEffect(() => {
    loadNovels();
  }, []);

  return (
    <div className="flex flex-1 h-full overflow-hidden">
      {/* Left Sidebar */}
      <div
        className="transition-all duration-300 ease-in-out overflow-hidden flex-shrink-0"
        style={{ width: showLeft ? "256px" : "0px" }}
      >
        <div className="w-64 h-full">
          <NovelSidebar />
        </div>
      </div>

      {/* Center: Editor */}
      <div className="flex-1 min-w-0">
        <Editor
          sidebarVisible={showLeft}
          onToggleSidebar={() => setShowLeft(!showLeft)}
        />
      </div>

      {/* Right Toggle */}
      <RightToggleBtn visible={showRight} onClick={() => setShowRight(!showRight)} />

      {/* Right Panels */}
      <div
        className="transition-all duration-300 ease-in-out flex-shrink-0"
        style={{ width: showRight ? "384px" : "44px" }}
      >
        {showRight ? (
          <div className="flex flex-col w-96 border-l border-gray-200 dark:border-gray-700 overflow-y-auto overflow-x-hidden h-full">
            {/* V4 Panels */}
            <PlannerPanel />
            <StoryGraphPanel />
            <ForeshadowingPanel />
            <NarrativeTimelinePanel />

            {/* V3 Panels */}
            <StylePanel />
            <NarrativePanel />

            {/* V2 Panels */}
            <MemoryPanel />

            {/* AI Panel (V2/V3/V4) */}
            <AIPanel />

            {/* History */}
            <GenerationHistory />
          </div>
        ) : (
          <RightPanelIconBar />
        )}
      </div>
    </div>
  );
}
