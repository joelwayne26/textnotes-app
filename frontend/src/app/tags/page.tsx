"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { tagsApi, notesApi } from "@/lib/api";
import { isAuthenticated, getUser } from "@/lib/auth";
import { Tag, Note } from "@/types";
import { 
  Tags as TagIcon, 
  Plus, 
  Trash2, 
  Edit3,
  X,
  Hash
} from "lucide-react";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Card from "@/components/ui/Card";

export default function TagsPage() {
  const router = useRouter();
  const [tags, setTags] = useState<Tag[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTagName, setNewTagName] = useState("");
  const [newTagColor, setNewTagColor] = useState("#6366f1");
  const [selectedTag, setSelectedTag] = useState<number | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState("");
  const [editColor, setEditColor] = useState("");

  const loadData = useCallback(async () => {
    try {
      const [tagsData, notesData] = await Promise.all([
        tagsApi.list(),
        notesApi.list({}),
      ]);
      setTags(tagsData);
      setNotes(notesData);
    } catch (err) {
      console.error("Failed to load data:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
      return;
    }
    loadData();
  }, [loadData, router]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!newTagName.trim()) return;

    try {
      await tagsApi.create({ 
        name: newTagName.trim(), 
        color: newTagColor 
      });
      setNewTagName("");
      setNewTagColor("#6366f1");
      setShowCreateForm(false);
      loadData();
    } catch (err) {
      console.error("Failed to create tag:", err);
    }
  }

  async function handleUpdate(tagId: number) {
    if (!editName.trim()) return;

    try {
      await tagsApi.update(tagId, { name: editName.trim(), color: editColor });
      setEditingId(null);
      loadData();
    } catch (err) {
      console.error("Failed to update tag:", err);
    }
  }

  async function handleDelete(tagId: number) {
    if (!confirm("Delete this tag? It will be removed from all notes.")) return;

    try {
      await tagsApi.delete(tagId);
      if (selectedTag === tagId) setSelectedTag(null);
      loadData();
    } catch (err) {
      console.error("Failed to delete tag:", err);
    }
  }

  // Get notes for selected tag
  const filteredNotes = selectedTag
    ? notes.filter(note => note.tags?.some(t => t.id === selectedTag))
    : [];

  // Count notes per tag
  const getNotesCountForTag = (tagId: number) => {
    return notes.filter(note => note.tags?.some(t => t.id === tagId)).length;
  };

  // Color options for tag creation
  const colorOptions = [
    "#6366f1", "#8b5cf6", "#ec4899", "#ef4444", 
    "#f97316", "#eab308", "#22c55e", "#14b8a6",
    "#06b6d4", "#3b82f6"
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-500">Loading tags...</div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-6xl mx-auto">
      {/* Page Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
            <TagIcon size={28} className="text-indigo-600" />
            Tags
          </h1>
          <p className="text-gray-500 mt-1">
            Categorize your notes with tags
          </p>
        </div>

        <Button
          onClick={() => setShowCreateForm(!showCreateForm)}
          variant="primary"
        >
          <Plus size={18} className="mr-1" />
          New Tag
        </Button>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Tags List */}
        <div className="lg:col-span-1">
          {/* Create Tag Form */}
          {showCreateForm && (
            <Card className="mb-4" padding="md">
              <form onSubmit={handleCreate} className="space-y-3">
                <Input
                  value={newTagName}
                  onChange={(e) => setNewTagName(e.target.value)}
                  placeholder="Tag name..."
                  autoFocus
                />
                
                {/* Color Picker */}
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-2">
                    Color
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {colorOptions.map((color) => (
                      <button
                        key={color}
                        type="button"
                        onClick={() => setNewTagColor(color)}
                        className={`w-7 h-7 rounded-full transition-transform ${
                          newTagColor === color ? "ring-2 ring-offset-2 ring-gray-400 scale-110" : ""
                        }`}
                        style={{ backgroundColor: color }}
                      />
                    ))}
                  </div>
                </div>

                <div className="flex gap-2 pt-2">
                  <Button type="submit" size="sm" variant="primary">
                    Create
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="ghost"
                    onClick={() => setShowCreateForm(false)}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </Card>
          )}

          {/* Tags List */}
          {tags.length === 0 ? (
            <Card className="text-center py-8">
              <Hash size={32} className="mx-auto text-gray-300 mb-3" />
              <p className="text-sm text-gray-500">No tags yet</p>
            </Card>
          ) : (
            <div className="space-y-2">
              {/* All Notes Option */}
              <button
                onClick={() => setSelectedTag(null)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  selectedTag === null
                    ? "bg-indigo-100 text-indigo-700"
                    : "hover:bg-gray-100 text-gray-700"
                }`}
              >
                <Hash size={16} />
                <span className="font-medium">All Tags</span>
                <span className="ml-auto text-xs bg-gray-200 px-2 py-0.5 rounded-full">
                  {notes.length}
                </span>
              </button>

              {tags.map((tag) => (
                <div
                  key={tag.id}
                  className={`group rounded-lg transition-colors ${
                    selectedTag === tag.id ? "bg-indigo-50" : ""
                  }`}
                >
                  {editingId === tag.id ? (
                    // Edit Mode
                    <div className="p-3 space-y-3">
                      <Input
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        autoFocus
                        size="sm"
                      />
                      <div className="flex gap-1">
                        {colorOptions.map((color) => (
                          <button
                            key={color}
                            type="button"
                            onClick={() => setEditColor(color)}
                            className={`w-5 h-5 rounded-full ${
                              editColor === color ? "ring-1.5 ring-offset-1 ring-gray-400" : ""
                            }`}
                            style={{ backgroundColor: color }}
                          />
                        ))}
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          onClick={() => handleUpdate(tag.id)}
                        >
                          Save
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => setEditingId(null)}
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  ) : (
                    // Display Mode
                    <button
                      onClick={() => setSelectedTag(tag.id)}
                      className="w-full flex items-center gap-3 px-4 py-3"
                    >
                      <span
                        className="w-4 h-4 rounded-full shrink-0"
                        style={{ backgroundColor: tag.color }}
                      />
                      <span className="font-medium truncate flex-1 text-left">
                        {tag.name}
                      </span>
                      <span className="text-xs text-gray-400">
                        {getNotesCountForTag(tag.id)} notes
                      </span>
                      
                      {/* Action buttons on hover */}
                      <div className="hidden group-hover:flex items-center gap-0.5">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setEditingId(tag.id);
                            setEditName(tag.name);
                            setEditColor(tag.color);
                          }}
                          className="p-1 rounded text-gray-400 hover:text-blue-500 hover:bg-blue-50"
                        >
                          <Edit3 size={12} />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(tag.id);
                          }}
                          className="p-1 rounded text-gray-400 hover:text-red-500 hover:bg-red-50"
                        >
                          <Trash2 size={12} />
                        </button>
                      </div>
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Notes with Selected Tag */}
        <div className="lg:col-span-2">
          {selectedTag ? (
            <>
              <div className="flex items-center gap-2 mb-4">
                <span
                  className="w-4 h-4 rounded-full"
                  style={{ backgroundColor: tags.find(t => t.id === selectedTag)?.color }}
                />
                <h2 className="text-lg font-semibold text-gray-900">
                  Notes tagged "{tags.find(t => t.id === selectedTag)?.name}"
                </h2>
                <button
                  onClick={() => setSelectedTag(null)}
                  className="ml-auto p-1 rounded hover:bg-gray-100"
                >
                  <X size={18} className="text-gray-400" />
                </button>
              </div>

              {filteredNotes.length === 0 ? (
                <Card className="text-center py-12">
                  <TagIcon size={40} className="mx-auto text-gray-300 mb-3" />
                  <p className="text-gray-500">No notes with this tag</p>
                </Card>
              ) : (
                <div className="space-y-3">
                  {filteredNotes.map((note) => (
                    <button
                      key={note.id}
                      onClick={() => router.push(`/notes/${note.id}`)}
                      className="w-full text-left Card hover:bg-gray-50 rounded-lg border border-gray-200 p-4 transition-colors"
                    >
                      <h3 className="font-medium text-gray-900">{note.title}</h3>
                      <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                        {note.content?.substring(0, 100)}...
                      </p>
                      <div className="mt-2 text-xs text-gray-400">
                        {new Date(note.updated_at || "").toLocaleDateString()}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </>
          ) : (
            <Card className="text-center py-12">
              <TagIcon size={48} className="mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Select a tag</h3>
              <p className="text-gray-500">
                Choose a tag from the left to see related notes
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
