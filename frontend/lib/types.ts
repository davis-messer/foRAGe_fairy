export type FileStatus = "uploading" | "ready" | "error";

export interface UploadedFile {
  id: string;
  name: string;
  size: number;
  uploadedAt: Date;
  status: FileStatus;
  selected: boolean;
  error?: string;
}

export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: Date;
  sources?: string[];
  error?: boolean;
}
