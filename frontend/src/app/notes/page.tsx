"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { notesApi, foldersApi, tagsApi } from "@/lib/api";
import { clearAuth, getUser, isAuthenticated } from "@/lib/auth";
import { Note, Folder, Tag } from "@/types";
import { Search, Plus, LogOut, Folder as FolderIcon, Tag as TagIcon, Pin, AlertCircle } from "lucide-react";

export default function NotesPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [notes, setNotes] = useState<Note[]>([]);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [query, setQuery] = useState("");
  const [selectedFolder, setSelectedFolder] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState(getUser());
  const [creatingNote, setCreatingNote] = useState(false);

  const loadData = useCallback(async () => {
    try {
      setError(null);
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
    } catch (err: any) {
      console.error("Failed to load data:", err);
      setError(err.message || "Failed to load data. Is the backend running?");
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

  // Auto-create note if ?new=true in URL
  useEffect(() => {
    if (searchParams.get("new") === "true" && !creatingNote) {
      createNote();
    }
  }, [searchParams]);

  function handleLogout() {
    clearAuth();
    router.push("/login");
  }

  async function createNote() {
    setCreatingNote(true);
    try {
      const note = await notesApi.create({
        title: "Untitled note",
        content: "",
        folder_id: selectedFolder || undefined,
      });
      router.push(`/notes/${note.id}`);
    } catch (err: any) {
      console.error("Failed to create note:", err);
      setError(err.message || "Failed to create note");
      setCreatingNote(false);
    }
  }

  // Show error state with retry
  if (error && !loading) {
    return (
      <div className="flex h-screen bg-gray-950 text-gray-100 items-center justify-center">
        <div className="text-center max-w-md p-8">
          <AlertCircle size={48} className="mx-auto text-red-500 mb-4" />
          <h2 className="text-xl font-bold text-white mb-2">Something went wrong</h2>
          <p className="text-gray-400 mb-6">{error}</p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => { setLoading(true); loadData(); }}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500"
            >
              Retry
            </button>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      {/* Main Content - No duplicate sidebar since Layout has one */}
      <main className="flex-1 flex flex-col">
        {/* Header */}
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
          
          {/* Folder Quick Filter */}
          <select
            value={selectedFolder || ""}
            onChange={(e) => setSelectedFolder(e.target.value ? Number(e.target.value) : null)}
            className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:border-indigo-500"
          >
            <option value="">All Folders</option>
            {folders.map(f => (
              <option key={f.id} value={f.id}>{f.name}</option>
            ))}
          </select>

          <button
            onClick={createNote}
            disabled={creatingNote}
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium hover:bg-indigo-500 transition disabled:opacity-50"
          >
            <Plus size={16} /> 
            {creatingNote ? "Creating..." : "New note"}
          </button>

          <span className="text-sm text-gray-500">{user?.username}</span>
        </header>

        {/* Tags Bar */}
        <div className="flex items-center gap-2 px-6 py-2 border-b border-gray-800 overflow-x-auto">
          <TagIcon size={14} className="text-gray-500 shrink-0" />
          {tags.length === 0 ? (
            <span className="text-xs text-gray-600">No tags yet</span>
          ) : (
            tags.map((t) => (
              <span
                key={t.id}
                className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium cursor-pointer hover:opacity-80 transition"
                style={{ backgroundColor: `${t.color}22`, color: t.color }}
                title={`Filter by ${t.name}`}
              >
                {t.name}
              </span>
            ))
          )}
        </div>

        {/* Notes Grid */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="text-center text-gray-500 py-20">
              <div className="animate-spin w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full mx-auto mb-4"></div>
              Loading notes…
            </div>
          ) : notes.length === 0 ? (
            <div className="text-center text-gray-500 py-20">
              <Pin size={48} className="mx-auto mb-4 opacity-30" />
              <p className="text-lg font-medium">No notes yet</p>
              <p className="mt-2 text-sm mb-6">Create your first note to get started</p>
              <button
                onClick={createNote}
                className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500"
              >
                <Plus size={16} /> Create your first note
              </button>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {notes.map((note) => (
                <Link
                  key={note.id}
                  href={`/notes/${note.id}`}
                  className="group rounded-xl border border-gray-800 bg-gray-900 p-4 hover:border-indigo-500/50 hover:bg-gray-900/80 transition-all hover:shadow-lg hover:shadow-indigo-500/10"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-medium text-white group-hover:text-indigo-300 line-clamp-1 flex-1">
                      {note.title || "Untitled"}
                    </h3>
                    {note.is_pinned && <Pin size={14} className="text-indigo-400 shrink-0" />}
                  </div>
                  
                  {note.content && (
                    <p className="mt-2 text-sm text-gray-500 line-clamp-2">
                      {note.content.replace(/[#*_`]/g, "").substring(0, 100)}
                    </p>
                  )}

                  <div className="mt-3 flex flex-wrap gap-1">
                    {note.tags?.map((t) => (
                      <span
                        key={t.id}
                        className="inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium"
                        style={{ backgroundColor: `${t.color}22`, color: t.color }}
                      >
                        {t.name}
                      </span>
                    ))}
                  </div>
                  
                  <div className="mt-3 pt-3 border-t border-gray-800 text-xs text-gray-500 flex justify-between">
                    <span>
                      {note.updated_at
                        ? new Date(note.updated_at).toLocaleDateString("en-US", { 
                            month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"
                          })
                        : ""}
                    </span>
                    {note.is_archived && (
                      <span className="text-yellow-500">Archived</span>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
