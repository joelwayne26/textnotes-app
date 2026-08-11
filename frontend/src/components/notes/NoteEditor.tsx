"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Save, ArrowLeft, Trash2, Pin, Archive, Tag as TagIcon, Plus, X } from "lucide-react";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Textarea from "@/components/ui/Textarea";
import { clsx } from "clsx";

interface NoteEditorProps {
  noteId?: string;
  initialData?: {
    title: string;
    content: string;
    is_pinned: boolean;
    is_archived: boolean;
  };
}

export default function NoteEditor({ noteId, initialData }: NoteEditorProps) {
  const router = useRouter();
  
  const [title, setTitle] = useState(initialData?.title || "");
  const [content, setContent] = useState(initialData?.content || "");
  const [isPinned, setIsPinned] = useState(initialData?.is_pinned || false);
  const [isArchived, setIsArchived] = useState(initialData?.is_archived || false);
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [showTagInput, setShowTagInput] = useState(false);
  const [newTag, setNewTag] = useState("");

  // Auto-save with debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      if (title || content) {
        handleSave();
      }
    }, 2000);

    return () => clearTimeout(timer);
  }, [title, content]);

  const handleSave = useCallback(async () => {
    setIsSaving(true);
    
    try {
      const url = noteId ? `/api/notes/${noteId}` : "/api/notes";
      const method = noteId ? "PUT" : "POST";
      
      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          title,
          content,
          is_pinned: isPinned,
          is_archived: isArchived,
        }),
      });

      if (response.ok) {
        setLastSaved(new Date());
      }
    } catch (error) {
      console.error("Failed to save:", error);
    } finally {
      setIsSaving(false);
    }
  }, [noteId, title, content, isPinned, isArchived]);

  const handleDelete = async () => {
    if (!noteId) return;
    
    if (confirm("Are you sure you want to delete this note?")) {
      try {
        await fetch(`/api/notes/${noteId}`, {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });
        router.push("/notes");
      } catch (error) {
        console.error("Failed to delete:", error);
      }
    }
  };

  const handleAddTag = () => {
    if (newTag.trim()) {
      // TODO: Implement tag adding logic
      setNewTag("");
      setShowTagInput(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <button
            onClick={() => router.back()}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            title="Go back"
          >
            <ArrowLeft size={18} />
          </button>

          <div className="h-6 w-px bg-gray-200 mx-1" />

          <button
            onClick={() => setIsPinned(!isPinned)}
            className={clsx(
              "p-2 rounded-lg transition-colors",
              isPinned
                ? "text-yellow-500 bg-yellow-50"
                : "text-gray-500 hover:bg-gray-100"
            )}
            title={isPinned ? "Unpin note" : "Pin note"}
          >
            <Pin size={18} fill={isPinned ? "currentColor" : "none"} />
          </button>

          <button
            onClick={() => setIsArchived(!isArchived)}
            className={clsx(
              "p-2 rounded-lg transition-colors",
              isArchived
                ? "text-blue-500 bg-blue-50"
                : "text-gray-500 hover:bg-gray-100"
            )}
            title={isArchived ? "Unarchive" : "Archive"}
          >
            <Archive size={18} />
          </button>
        </div>

        <div className="flex items-center gap-2">
          {/* Status indicator */}
          <span className="text-xs text-gray-500 mr-2">
            {isSaving ? (
              <span className="flex items-center gap-1">
                <span className="animate-spin">⏳</span> Saving...
              </span>
            ) : lastSaved ? (
              `Saved ${lastSaved.toLocaleTimeString()}`
            ) : (
              ""
            )}
          </span>

          <Button
            variant="primary"
            size="sm"
            onClick={handleSave}
            disabled={isSaving}
          >
            <Save size={16} className="mr-1" />
            Save
          </Button>

          {noteId && (
            <button
              onClick={handleDelete}
              className="p-2 rounded-lg text-red-500 hover:bg-red-50 transition-colors"
              title="Delete note"
            >
              <Trash2 size={18} />
            </button>
          )}
        </div>
      </div>

      {/* Editor Content */}
      <div className="flex-1 overflow-y-auto p-4 lg:p-8 max-w-4xl mx-auto w-full">
        {/* Title Input */}
        <Input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Note title..."
          className="text-2xl font-bold border-0 px-0 focus:ring-0 mb-4"
          id="note-title"
        />

        {/* Tags */}
        <div className="flex items-center gap-2 mb-4">
          <button
            onClick={() => setShowTagInput(!showTagInput)}
            className="flex items-center gap-1 text-sm text-gray-500 hover:text-indigo-600 transition-colors"
          >
            <TagIcon size={14} />
            Add tag
          </button>

          {showTagInput && (
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                placeholder="Tag name..."
                className="px-2 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                onKeyDown={(e) => e.key === "Enter" && handleAddTag()}
                autoFocus
              />
              <button
                onClick={handleAddTag}
                className="p-1 text-green-600 hover:bg-green-50 rounded"
              >
                <Plus size={14} />
              </button>
              <button
                onClick={() => setShowTagInput(false)}
                className="p-1 text-gray-400 hover:bg-gray-100 rounded"
              >
                <X size={14} />
              </button>
            </div>
          )}
        </div>

        {/* Content Editor */}
        <Textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Start writing your note... (Markdown supported)"
          className="min-h-[60vh] border-0 px-0 focus:ring-0 resize-none text-gray-800 leading-relaxed"
          id="note-content"
        />
      </div>
    </div>
  );
}
