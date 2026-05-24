"use client";

import { useEffect } from "react";
import { useNovelStore } from "@/app/store/useNovelStore";
import NovelSidebar from "@/app/components/NovelSidebar";
import Editor from "@/app/components/Editor";
import AIPanel from "@/app/components/AIPanel";
import GenerationHistory from "@/app/components/GenerationHistory";

export default function Home() {
  const loadNovels = useNovelStore((s) => s.loadNovels);

  useEffect(() => {
    loadNovels();
  }, []);

  return (
    <div className="flex flex-1 h-full overflow-hidden">
      {/* Left: Novel & Chapter list */}
      <NovelSidebar />

      {/* Center: Editor */}
      <Editor />

      {/* Right: AI Panel */}
      <div className="flex flex-col w-80 border-l border-gray-200 dark:border-gray-700">
        <AIPanel />
        <GenerationHistory />
      </div>
    </div>
  );
}
