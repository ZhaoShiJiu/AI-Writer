"use client";

import { useEffect, useCallback, useRef } from "react";
import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Placeholder from "@tiptap/extension-placeholder";
import { useNovelStore } from "@/app/store/useNovelStore";

export default function Editor() {
  const { currentChapter, saveChapter } = useNovelStore();
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: { levels: [1, 2, 3] },
      }),
      Placeholder.configure({
        placeholder: "开始创作你的故事...",
      }),
    ],
    content: currentChapter?.content || "",
    editorProps: {
      attributes: {
        class: "prose prose-lg dark:prose-invert max-w-none focus:outline-none min-h-[60vh] px-8 py-6",
      },
    },
  });

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
      <div className="flex-1 flex items-center justify-center text-gray-400 dark:text-gray-500">
        <div className="text-center">
          <p className="text-lg">选择一个章节开始写作</p>
          <p className="text-sm mt-2">或从左侧创建一个新的小说和章节</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="flex items-center gap-1 px-4 py-2 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="flex items-center gap-0.5">
          <button
            onClick={() => editor?.chain().focus().toggleBold().run()}
            className={`p-1.5 rounded text-sm ${
              editor?.isActive("bold")
                ? "bg-gray-200 dark:bg-gray-600"
                : "hover:bg-gray-100 dark:hover:bg-gray-700"
            }`}
            title="加粗 (Ctrl+B)"
          >
            <strong>B</strong>
          </button>
          <button
            onClick={() => editor?.chain().focus().toggleItalic().run()}
            className={`p-1.5 rounded text-sm ${
              editor?.isActive("italic")
                ? "bg-gray-200 dark:bg-gray-600"
                : "hover:bg-gray-100 dark:hover:bg-gray-700"
            }`}
            title="斜体 (Ctrl+I)"
          >
            <em>I</em>
          </button>
          <span className="w-px h-5 bg-gray-300 dark:bg-gray-600 mx-1" />
          <button
            onClick={() => editor?.chain().focus().toggleHeading({ level: 2 }).run()}
            className={`p-1.5 rounded text-xs font-semibold ${
              editor?.isActive("heading", { level: 2 })
                ? "bg-gray-200 dark:bg-gray-600"
                : "hover:bg-gray-100 dark:hover:bg-gray-700"
            }`}
          >
            H2
          </button>
          <button
            onClick={() => editor?.chain().focus().toggleHeading({ level: 3 }).run()}
            className={`p-1.5 rounded text-xs font-semibold ${
              editor?.isActive("heading", { level: 3 })
                ? "bg-gray-200 dark:bg-gray-600"
                : "hover:bg-gray-100 dark:hover:bg-gray-700"
            }`}
          >
            H3
          </button>
        </div>
        <div className="flex-1" />
        <span className="text-xs text-gray-400">自动保存</span>
      </div>

      <div className="flex-1 overflow-y-auto">
        <EditorContent editor={editor} />
      </div>
    </div>
  );
}
