const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public details?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

export async function api<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: HeadersInit = {
    ...(options.headers || {}),
  };

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  // Don't set Content-Type for FormData
  if (!(options.body instanceof FormData)) {
    (headers as Record<string, string>)["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let errorBody: any = {};
    try {
      errorBody = await res.json();
    } catch {
      /* ignore */
    }
    throw new ApiError(
      res.status,
      errorBody.error || res.statusText,
      errorBody.details
    );
  }

  // Handle 204
  if (res.status === 204) return {} as T;

  return res.json() as Promise<T>;
}

// Auth
export const authApi = {
  register: (data: { email: string; username: string; password: string }) =>
    api<import("@/types").AuthResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  login: (data: { email: string; password: string }) =>
    api<import("@/types").AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  me: () => api<import("@/types").User>("/api/auth/me"),
};

// Notes
export const notesApi = {
  list: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return api<import("@/types").Note[]>(`/api/notes${qs}`);
  },
  get: (id: number) => api<import("@/types").Note>(`/api/notes/${id}`),
  create: (data: Partial<import("@/types").Note> & { tag_ids?: number[] }) =>
    api<import("@/types").Note>("/api/notes", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: Partial<import("@/types").Note> & { tag_ids?: number[] }) =>
    api<import("@/types").Note>(`/api/notes/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    api<{ message: string }>(`/api/notes/${id}`, { method: "DELETE" }),
};

// Folders
export const foldersApi = {
  list: () => api<import("@/types").Folder[]>("/api/folders"),
  create: (data: { name: string; parent_id?: number | null }) =>
    api<import("@/types").Folder>("/api/folders", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: { name: string; parent_id?: number | null }) =>
    api<import("@/types").Folder>(`/api/folders/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    api<{ message: string }>(`/api/folders/${id}`, { method: "DELETE" }),
};

// Tags
export const tagsApi = {
  list: () => api<import("@/types").Tag[]>("/api/tags"),
  create: (data: { name: string; color?: string }) =>
    api<import("@/types").Tag>("/api/tags", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: { name: string; color?: string }) =>
    api<import("@/types").Tag>(`/api/tags/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    api<{ message: string }>(`/api/tags/${id}`, { method: "DELETE" }),
};

// Attachments
export const attachmentsApi = {
  upload: (noteId: number, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return api<import("@/types").Attachment>(`/api/attachments/notes/${noteId}`, {
      method: "POST",
      body: form,
    });
  },
  delete: (id: number) =>
    api<{ message: string }>(`/api/attachments/${id}`, { method: "DELETE" }),
};
