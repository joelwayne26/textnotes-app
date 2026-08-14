"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { notesApi, attachmentsApi } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { Note } from "@/types";
import { ArrowLeft, Save, Trash2, Pin, Upload, Paperclip } from "lucide-react";

export default function NoteDetailPage() {
  const router = useRouter();
  const params = useParams();
  const noteId = Number(params.id);

  const [note, setNote] = useState<Note | null>(null);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [saving, setSaving] = useState(false);
  const [preview, setPreview] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadNote = useCallback(async () => {
    try {
      const data = await notesApi.get(noteId);
      setNote(data);
      setTitle(data.title);
      setContent(data.content || "");
    } catch {
      router.push("/notes");
    } finally {
      setLoading(false);
    }
  }, [noteId, router]);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
      return;
    }
    loadNote();
  }, [loadNote, router]);

  async function handleSave() {
    setSaving(true);
    try {
      const updated = await notesApi.update(noteId, { title, content });
      setNote(updated);
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!confirm("Delete this note permanently?")) return;
    try {
      await notesApi.delete(noteId);
      router.push("/notes");
    } catch (err) {
      console.error(err);
    }
  }

  async function togglePin() {
    if (!note) return;
    try {
      const updated = await notesApi.update(noteId, { is_pinned: !note.is_pinned });
      setNote(updated);
    } catch (err) {
      console.error(err);
    }
  }

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const att = await attachmentsApi.upload(noteId, file);
      setNote((prev) =>
        prev ? { ...prev, attachments: [...prev.attachments, att] } : prev
      );
    } catch (err) {
      console.error(err);
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-950 text-gray-400">
        Loading…
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col bg-gray-950 text-gray-100">
      {/* Toolbar */}
      <header className="flex items-center gap-3 border-b border-gray-800 px-4 py-3">
        <Link
          href="/notes"
          className="rounded-lg p-2 text-gray-400 hover:bg-gray-800 hover:text-white transition"
        >
          <ArrowLeft size={18} />
        </Link>

        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="flex-1 bg-transparent text-lg font-medium focus:outline-none"
          placeholder="Note title"
        />

        <button
          onClick={() => setPreview(!preview)}
          className="rounded-lg px-3 py-1.5 text-sm text-gray-400 hover:bg-gray-800 transition"
        >
          {preview ? "Edit" : "Preview"}
        </button>

        <button
          onClick={togglePin}
          className={`rounded-lg p-2 transition ${
            note?.is_pinned ? "text-indigo-400" : "text-gray-400 hover:text-white"
          }`}
          title="Pin note"
        >
          <Pin size={18} />
        </button>

        <label className="rounded-lg p-2 text-gray-400 hover:bg-gray-800 hover:text-white transition cursor-pointer">
          <Upload size={18} />
          <input type="file" className="hidden" onChange={handleUpload} />
        </label>

        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium hover:bg-indigo-500 disabled:opacity-50 transition"
        >
          <Save size={16} /> {saving ? "Saving…" : "Save"}
        </button>

        <button
          onClick={handleDelete}
          className="rounded-lg p-2 text-gray-400 hover:bg-red-500/20 hover:text-red-400 transition"
        >
          <Trash2 size={18} />
        </button>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {preview ? (
          <div className="mx-auto max-w-3xl px-6 py-8 prose">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          </div>
        ) : (
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="h-full w-full resize-none bg-transparent px-6 py-8 font-mono text-sm leading-relaxed focus:outline-none"
            placeholder="Write your markdown here…"
          />
        )}
      </div>

      {/* Attachments bar */}
      {note && note.attachments.length > 0 && (
        <div className="border-t border-gray-800 px-4 py-2 flex items-center gap-3 overflow-x-auto">
          <Paperclip size={14} className="text-gray-500 shrink-0" />
          {note.attachments.map((a) => (
            <a
              key={a.id}
              href={`${process.env.NEXT_PUBLIC_API_URL}${a.url}`}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-indigo-400 hover:underline whitespace-nowrap"
            >
              {a.original_filename}
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
