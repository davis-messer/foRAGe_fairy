const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface ServerFile {
  id: string;
  name: string;
  size: number;
  uploaded_at: string;
}

export interface ChatResult {
  answer: string;
  sources: string[];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, init);
  } catch {
    throw new Error(
      `Can't reach the backend at ${API_URL}. Is the API server running?`,
    );
  }
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed (${res.status})`);
  }
  return (res.status === 204 ? undefined : await res.json()) as T;
}

export function listFiles(): Promise<ServerFile[]> {
  return request("/api/files");
}

export function uploadFile(file: File): Promise<ServerFile> {
  const body = new FormData();
  body.append("file", file);
  return request("/api/files", { method: "POST", body });
}

export function deleteFile(id: string): Promise<void> {
  return request(`/api/files/${encodeURIComponent(id)}`, { method: "DELETE" });
}

export function sendChatMessage(
  question: string,
  fileIds: string[],
): Promise<ChatResult> {
  return request("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, file_ids: fileIds }),
  });
}
