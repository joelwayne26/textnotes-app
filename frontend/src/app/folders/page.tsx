"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { foldersApi } from "@/lib/api";
import { isAuthenticated, getUser } from "@/lib/auth";
import { Folder } from "@/types";
import { 
  FolderOpen, 
  Plus, 
  Trash2, 
  Edit3, 
  ChevronRight,
  FileText,
  ArrowLeft
} from "lucide-react";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Card from "@/components/ui/Card";

export default function FoldersPage() {
  const router = useRouter();
  const [folders, setFolders] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newFolderName, setNewFolderName] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState("");
  const [user, setUser] = useState(getUser());

  const loadFolders = useCallback(async () => {
    try {
      const data = await foldersApi.list();
      setFolders(data);
    } catch (err) {
      console.error("Failed to load folders:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
      return;
    }
    loadFolders();
  }, [loadFolders, router]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!newFolderName.trim()) return;

    try {
      await foldersApi.create({ name: newFolderName.trim() });
      setNewFolderName("");
      setShowCreateForm(false);
      loadFolders();
    } catch (err) {
      console.error("Failed to create folder:", err);
    }
  }

  async function handleUpdate(folderId: number) {
    if (!editName.trim()) return;

    try {
      await foldersApi.update(folderId, { name: editName.trim() });
      setEditingId(null);
      loadFolders();
    } catch (err) {
      console.error("Failed to update folder:", err);
    }
  }

  async function handleDelete(folderId: number) {
    if (!confirm("Delete this folder? Notes inside will be unorganized.")) return;

    try {
      await foldersApi.delete(folderId);
      loadFolders();
    } catch (err) {
      console.error("Failed to delete folder:", err);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-500">Loading folders...</div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-4xl mx-auto">
      {/* Page Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
            <FolderOpen size={28} className="text-indigo-600" />
            Folders
          </h1>
          <p className="text-gray-500 mt-1">
            Organize your notes into folders
          </p>
        </div>

        <Button
          onClick={() => setShowCreateForm(!showCreateForm)}
          variant="primary"
        >
          <Plus size={18} className="mr-1" />
          New Folder
        </Button>
      </div>

      {/* Create Folder Form */}
      {showCreateForm && (
        <Card className="mb-6" padding="md">
          <form onSubmit={handleCreate} className="flex gap-3">
            <Input
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              placeholder="Folder name..."
              autoFocus
              className="flex-1"
            />
            <Button type="submit" variant="primary">
              Create
            </Button>
            <Button
              type="button"
              variant="ghost"
              onClick={() => setShowCreateForm(false)}
            >
              Cancel
            </Button>
          </form>
        </Card>
      )}

      {/* Folders List */}
      {folders.length === 0 ? (
        <Card className="text-center py-12">
          <FolderOpen size={48} className="mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No folders yet</h3>
          <p className="text-gray-500 mb-4">
            Create your first folder to organize your notes
          </p>
          <Button onClick={() => setShowCreateForm(true)} variant="secondary">
            <Plus size={16} className="mr-1" />
            Create Folder
          </Button>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {folders.map((folder) => (
            <Card key={folder.id} hover padding="md">
              {editingId === folder.id ? (
                // Edit Mode
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleUpdate(folder.id);
                  }}
                  className="space-y-3"
                >
                  <Input
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    autoFocus
                  />
                  <div className="flex gap-2">
                    <Button type="submit" size="sm" variant="primary">
                      Save
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      onClick={() => setEditingId(null)}
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              ) : (
                // Display Mode
                <>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3 min-w-0">
                      <FolderOpen size={20} className="text-indigo-500 shrink-0" />
                      <h3 className="font-semibold text-gray-900 truncate">
                        {folder.name}
                      </h3>
                    </div>

                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => {
                          setEditingId(folder.id);
                          setEditName(folder.name);
                        }}
                        className="p-1.5 rounded-md text-gray-400 hover:text-blue-500 hover:bg-blue-50 transition-colors"
                        title="Rename"
                      >
                        <Edit3 size={14} />
                      </button>
                      <button
                        onClick={() => handleDelete(folder.id)}
                        className="p-1.5 rounded-md text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                        title="Delete"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>

                  <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <FileText size={12} />
                      {folder.notes_count || 0} notes
                    </span>
                    <span>
                      Created {new Date(folder.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  <button
                    onClick={() => router.push(`/notes?folder=${folder.id}`)}
                    className="mt-3 w-full flex items-center justify-center gap-1 text-sm text-indigo-600 hover:text-indigo-700 font-medium py-2 rounded-lg hover:bg-indigo-50 transition-colors"
                  >
                    View Notes
                    <ChevronRight size={14} />
                  </button>
                </>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
