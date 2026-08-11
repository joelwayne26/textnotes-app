"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { notesApi, foldersApi, tagsApi } from "@/lib/api";
import { clearAuth, getUser, isAuthenticated } from "@/lib/auth";
import { Note, Folder, Tag } from "@/types";
import { Search, Plus, LogOut, Folder as FolderIcon, Tag as TagIcon, Pin } from "lucide-react";

export default function NotesPage() {
  const router = useRouter();
  const [notes, setNotes] = useState<Note[]>([]);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [query, setQuery] = useState("");
  const [selectedFolder, setSelectedFolder] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(getUser());

  const loadData = useCallback(async () => {
    try {
      const params: Record<string, string> = {};
      if (query) params.q = query;
      if (selectedFolder) params.folder_id = String(selectedFolder);

      const [notesData, foldersData, tagsData] = await Promise.all([
        notesApi.list(params),
        foldersApi.list(),
        tagsApi.list(),
      ]);
      setNotes(notesData);
      setFolders(foldersData);
      setTags(tagsData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [query, selectedFolder]);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
      return;
    }
    loadData();
  }, [loadData, router]);

  function handleLogout() {
    clearAuth();
    router.push("/login");
  }

  async function createNote() {
    try {
      const note = await notesApi.create({
        title: "Untitled note",
        content: "",
        folder_id: selectedFolder || undefined,
      });
      router.push(`/notes/${note.id}`);
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      {/* Sidebar */}
      <aside className="w-64 border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <h1 className="text-xl font-bold">Notes</h1>
          <p className="text-xs text-gray-500 mt-1">{user?.username}</p>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-4">
          <div>
            <button
              onClick={() => setSelectedFolder(null)}
              className={`w-full flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition ${
                selectedFolder === null ? "bg-indigo-600/20 text-indigo-300" : "hover:bg-gray-800"
              }`}
            >
              All notes
            </button>
          </div>

          <div>
            <div className="flex items-center gap-2 px-3 mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500">
              <FolderIcon size={14} /> Folders
            </div>
            {folders.map((f) => (
              <button
                key={f.id}
                onClick={() => setSelectedFolder(f.id)}
                className={`w-full flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition ${
                  selectedFolder === f.id ? "bg-indigo-600/20 text-indigo-300" : "hover:bg-gray-800"
                }`}
              >
                {f.name}
              </button>
            ))}
          </div>

          <div>
            <div className="flex items-center gap-2 px-3 mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500">
              <TagIcon size={14} /> Tags
            </div>
            <div className="flex flex-wrap gap-1.5 px-2">
              {tags.map((t) => (
                <span
                  key={t.id}
                  className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
                  style={{ backgroundColor: `${t.color}22`, color: t.color }}
                >
                  {t.name}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="p-3 border-t border-gray-800">
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-gray-400 hover:bg-gray-800 hover:text-white transition"
          >
            <LogOut size={16} /> Log out
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col">
        <header className="flex items-center gap-4 border-b border-gray-800 px-6 py-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
            <input
              type="search"
              placeholder="Search notes…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full rounded-lg border border-gray-700 bg-gray-900 pl-10 pr-4 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <button
            onClick={createNote}
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium hover:bg-indigo-500 transition"
          >
            <Plus size={16} /> New note
          </button>
        </header>

        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="text-center text-gray-500 py-20">Loading notes…</div>
          ) : notes.length === 0 ? (
            <div className="text-center text-gray-500 py-20">
              <p className="text-lg">No notes yet</p>
              <p className="mt-2 text-sm">Create your first note to get started</p>
            </div>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {notes.map((note) => (
                <Link
                  key={note.id}
                  href={`/notes/${note.id}`}
                  className="group rounded-xl border border-gray-800 bg-gray-900 p-4 hover:border-indigo-500/50 hover:bg-gray-900/80 transition"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-medium text-white group-hover:text-indigo-300 line-clamp-1">
                      {note.title}
                    </h3>
                    {note.is_pinned && <Pin size={14} className="text-indigo-400 shrink-0" />}
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {note.tags.map((t) => (
                      <span
                        key={t.id}
                        className="inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium"
                        style={{ backgroundColor: `${t.color}22`, color: t.color }}
                      >
                        {t.name}
                      </span>
                    ))}
                  </div>
                  <p className="mt-3 text-xs text-gray-500">
                    {note.updated_at
                      ? new Date(note.updated_at).toLocaleDateString()
                      : ""}
                  </p>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
