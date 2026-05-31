"use client";

import { useEffect, useCallback, useRef, useState } from "react";
import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Placeholder from "@tiptap/extension-placeholder";
import { useNovelStore, setEditorInstance } from "@/app/store/useNovelStore";

interface EditorProps {
  sidebarVisible?: boolean;
  onToggleSidebar?: () => void;
}

function SidebarToggleIcon({ visible }: { visible: boolean }) {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      {visible ? (
        /* 侧边栏可见 → 显示"收起"图标（竖条 + 向左箭头） */
        <>
          <rect x="3" y="4" width="12" height="16" rx="1.5" />
          <line x1="9" y1="9" x2="9" y2="15" />
          <polyline points="13,9 16,12 13,15" />
        </>
      ) : (
        /* 侧边栏隐藏 → 显示"展开"图标（竖条 + 向右箭头） */
        <>
          <rect x="9" y="4" width="12" height="16" rx="1.5" />
          <line x1="15" y1="9" x2="15" y2="15" />
          <polyline points="11,9 8,12 11,15" />
        </>
      )}
    </svg>
  );
}

export default function Editor({ sidebarVisible, onToggleSidebar }: EditorProps) {
  const { currentChapter, saveChapter, setSelection, clearSelection, polishMode, setPolishMode, selectedText } = useNovelStore();
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [floatPos, setFloatPos] = useState<{ x: number; y: number } | null>(null);

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: false,
        bold: false,
        italic: false,
        strike: false,
        code: false,
        blockquote: false,
      }),
      Placeholder.configure({
        placeholder: "开始创作你的故事...",
      }),
    ],
    content: currentChapter?.content || "",
    immediatelyRender: true,
    editorProps: {
      attributes: {
        class: "prose prose-lg dark:prose-invert max-w-none focus:outline-none min-h-[60vh] px-8 py-6",
      },
    },
  });

  // Register editor instance for polish replace
  useEffect(() => {
    setEditorInstance(editor);
    return () => setEditorInstance(null);
  }, [editor]);

  // Native selectionchange — reads DOM selection + posAtDOM, not editor.state.selection
  useEffect(() => {
    if (!editor) return;

    const handleSelectionChange = () => {
      const sel = window.getSelection();
      if (!sel || sel.isCollapsed || sel.rangeCount === 0) {
        // 润色模式下不清除选中状态——用户正在 AIPanel 中填写润色要求
        if (!useNovelStore.getState().polishMode) {
          clearSelection();
          setFloatPos(null);
        }
        return;
      }

      const editorDOM = editor.view.dom;
      const anchorNode = sel.anchorNode;
      if (!anchorNode || !editorDOM.contains(anchorNode)) return;

      // Map DOM positions to ProseMirror positions
      let from: number;
      let to: number;
      try {
        from = editor.view.posAtDOM(sel.anchorNode!, sel.anchorOffset);
        to = editor.view.posAtDOM(sel.focusNode!, sel.focusOffset);
      } catch {
        return; // Selection outside valid ProseMirror positions
      }

      if (from === to) {
        clearSelection();
        setFloatPos(null);
        return;
      }

      const realFrom = Math.min(from, to);
      const realTo = Math.max(from, to);

      const text = editor.state.doc.textBetween(realFrom, realTo, "\n");
      if (!text.trim()) {
        clearSelection();
        setFloatPos(null);
        return;
      }

      const beforeStart = Math.max(0, realFrom - 300);
      const contextBefore = editor.state.doc.textBetween(beforeStart, realFrom, "\n");
      const docSize = editor.state.doc.content.size;
      const afterEnd = Math.min(docSize, realTo + 300);
      const contextAfter = editor.state.doc.textBetween(realTo, afterEnd, "\n");

      setSelection(text, realFrom, realTo, contextBefore, contextAfter);

      const endCoords = editor.view.coordsAtPos(realTo);
      const containerRect = containerRef.current?.getBoundingClientRect();
      if (containerRect) {
        setFloatPos({
          x: endCoords.right - containerRect.left + 8,
          y: endCoords.top - containerRect.top - 4,
        });
      }
    };

    document.addEventListener("selectionchange", handleSelectionChange);
    return () => document.removeEventListener("selectionchange", handleSelectionChange);
  }, [editor, setSelection, clearSelection]);

  // Sync editor content when switching chapters
  useEffect(() => {
    if (editor && currentChapter) {
      const currentContent = editor.getHTML();
      if (currentContent !== currentChapter.content) {
        editor.commands.setContent(currentChapter.content || "");
      }
    }
  }, [currentChapter?.id]);

  const handleSave = useCallback(() => {
    if (editor) {
      saveChapter(editor.getHTML());
    }
  }, [editor, saveChapter]);

  // Debounced auto-save on every edit
  useEffect(() => {
    if (!editor) return;

    const onUpdate = () => {
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => {
        saveChapter(editor.getHTML());
      }, 1500);
    };

    editor.on("update", onUpdate);
    return () => {
      editor.off("update", onUpdate);
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [editor, saveChapter]);

  // Keyboard shortcut: Ctrl+S to save
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault();
        handleSave();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [handleSave]);

  if (!currentChapter) {
    return (
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Minimal top bar with sidebar toggle */}
        {onToggleSidebar && (
          <div className="flex items-center px-4 py-1.5 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
            <button
              onClick={onToggleSidebar}
              className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
              title={sidebarVisible ? "收起侧边栏" : "展开侧边栏"}
            >
              <SidebarToggleIcon visible={!!sidebarVisible} />
            </button>
            <div className="flex-1" />
          </div>
        )}
        <div className="flex-1 flex items-center justify-center text-gray-400 dark:text-gray-500">
          <div className="text-center">
            <p className="text-lg">选择一个章节开始写作</p>
            <p className="text-sm mt-2">或从左侧创建一个新的小说和章节</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-2 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <button
          onClick={handleSave}
          className="px-3 py-1 text-xs font-medium bg-blue-500 hover:bg-blue-600 text-white rounded transition-colors"
          title="保存 (Ctrl+S)"
        >
          保存
        </button>

        {/* vertical divider */}
        {onToggleSidebar && (
          <div className="w-px h-5 bg-gray-300 dark:bg-gray-600 mx-0.5" />
        )}

        {/* sidebar toggle */}
        {onToggleSidebar && (
          <button
            onClick={onToggleSidebar}
            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
            title={sidebarVisible ? "收起侧边栏" : "展开侧边栏"}
          >
            <SidebarToggleIcon visible={!!sidebarVisible} />
          </button>
        )}

        <div className="flex-1" />
        <span className="text-xs text-gray-400">自动保存 (1.5s)</span>
      </div>

      <div ref={containerRef} className="flex-1 overflow-y-auto relative">
        <EditorContent editor={editor} />

        {/* Floating Polish Button */}
        {floatPos && selectedText && !polishMode && (
          <button
            onClick={() => setPolishMode(true)}
            className="absolute z-50 px-2.5 py-1 text-xs font-medium bg-blue-500 hover:bg-blue-600 text-white rounded shadow-lg transition-colors whitespace-nowrap"
            style={{ left: floatPos.x, top: floatPos.y }}
          >
            润色
          </button>
        )}
      </div>
    </div>
  );
}
