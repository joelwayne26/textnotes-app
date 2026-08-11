export interface User {
  id: number;
  email: string;
  username: string;
  created_at: string | null;
}

export interface Tag {
  id: number;
  name: string;
  color: string;
  owner_id: number;
}

export interface Attachment {
  id: number;
  filename: string;
  original_filename: string;
  content_type: string;
  size: number;
  url: string;
  created_at: string | null;
}

export interface Note {
  id: number;
  title: string;
  content?: string;
  is_pinned: boolean;
  is_archived: boolean;
  owner_id: number;
  folder_id: number | null;
  tags: Tag[];
  attachments: Attachment[];
  created_at: string | null;
  updated_at: string | null;
}

export interface Folder {
  id: number;
  name: string;
  parent_id: number | null;
  owner_id: number;
  children?: Folder[];
  created_at: string | null;
  updated_at: string | null;
}

export interface AuthResponse {
  message: string;
  user: User;
  access_token: string;
}
