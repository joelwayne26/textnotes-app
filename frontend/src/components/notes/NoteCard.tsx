"use client";

import Link from "next/link";
import { Pin, Archive, MoreVertical, Clock, Tag, FolderOpen } from "lucide-react";
import Card from "@/components/ui/Card";
import { clsx } from "clsx";
import type { Note } from "@/types/index";

interface NoteCardProps {
  note: Note;
  onPin?: (id: number) => void;
  onArchive?: (id: number) => void;
  onDelete?: (id: number) => void;
}

export default function NoteCard({ note, onPin, onArchive, onDelete }: NoteCardProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return "Today";
    if (days === 1) return "Yesterday";
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  };

  // Strip markdown for preview
  const getPreview = (content: string) => {
    return content
      .replace(/[#*_`~\[\]]/g, "")
      .substring(0, 150)
      .trim() + (content.length > 150 ? "..." : "");
  };

  return (
    <Link href={`/notes/${note.id}`}>
      <Card hover className="group h-full cursor-pointer">
        {/* Header */}
        <div className="flex items-start justify-between gap-2 mb-3">
          <h3 className="font-semibold text-gray-900 line-clamp-1 flex-1">
            {note.title || "Untitled Note"}
          </h3>
          
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            {onPin && (
              <button
                onClick={(e) => {
                  e.preventDefault();
                  onPin(note.id);
                }}
                className={clsx(
                  "p-1.5 rounded-md transition-colors",
                  note.is_pinned
                    ? "text-yellow-500 bg-yellow-50"
                    : "text-gray-400 hover:text-yellow-500 hover:bg-gray-50"
                )}
                title={note.is_pinned ? "Unpin" : "Pin"}
              >
                <Pin size={14} fill={note.is_pinned ? "currentColor" : "none"} />
              </button>
            )}
            
            {onArchive && (
              <button
                onClick={(e) => {
                  e.preventDefault();
                  onArchive(note.id);
                }}
                className="p-1.5 rounded-md text-gray-400 hover:text-blue-500 hover:bg-gray-50 transition-colors"
                title="Archive"
              >
                <Archive size={14} />
              </button>
            )}

            <button
              onClick={(e) => {
                e.preventDefault();
                onDelete?.(note.id);
              }}
              className="p-1.5 rounded-md text-gray-400 hover:text-red-500 hover:bg-gray-50 transition-colors"
            >
              <MoreVertical size={14} />
            </button>
          </div>
        </div>

        {/* Preview */}
        {note.content && (
          <p className="text-sm text-gray-600 mb-4 line-clamp-4 whitespace-pre-wrap">
            {getPreview(note.content)}
          </p>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between text-xs text-gray-500 pt-3 border-t border-gray-100">
          <div className="flex items-center gap-1">
            <Clock size={12} />
            <span>{formatDate(note.updated_at || note.created_at)}</span>
          </div>

          <div className="flex items-center gap-2">
            {note.tags && note.tags.length > 0 && (
              <div className="flex items-center gap-1">
                <Tag size={12} />
                <span>{note.tags.length}</span>
              </div>
            )}
            
            {note.folder_id && (
              <div className="flex items-center gap-1">
                <FolderOpen size={12} />
              </div>
            )}
          </div>
        </div>
      </Card>
    </Link>
  );
}
