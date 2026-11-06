"use client";

import { useRef, useState, type DragEvent } from "react";
import { deleteFile, uploadFile } from "@/lib/api";
import { fileExtension, formatBytes } from "@/lib/format";
import type { UploadedFile } from "@/lib/types";
import { TrashIcon, UploadIcon } from "./Icons";
import styles from "./FileList.module.css";

const ACCEPTED = ".pdf,.docx,.txt,.md";

interface FileListProps {
  files: UploadedFile[];
  onChange: (update: (prev: UploadedFile[]) => UploadedFile[]) => void;
  loadError?: string | null;
}

export default function FileList({ files, onChange, loadError }: FileListProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const update = (id: string, patch: Partial<UploadedFile>) =>
    onChange((prev) => prev.map((f) => (f.id === id ? { ...f, ...patch } : f)));

  const addFiles = (list: FileList | null) => {
    if (!list) return;
    const incoming = Array.from(list).map((file) => ({
      file,
      entry: {
        id: crypto.randomUUID(),
        name: file.name,
        size: file.size,
        uploadedAt: new Date(),
        status: "uploading",
        selected: true,
      } satisfies UploadedFile,
    }));
    onChange((prev) => [...incoming.map((i) => i.entry), ...prev]);
    for (const { file, entry } of incoming) {
      uploadFile(file)
        .then((saved) =>
          onChange((prev) =>
            prev
              .filter((f) => f.id !== saved.id)
              .map((f) =>
                f.id === entry.id
                  ? {
                      ...f,
                      id: saved.id,
                      size: saved.size,
                      uploadedAt: new Date(saved.uploaded_at),
                      status: "ready",
                    }
                  : f,
              ),
          ),
        )
        .catch((err: Error) =>
          update(entry.id, { status: "error", error: err.message }),
        );
    }
  };

  const toggle = (id: string) =>
    onChange((prev) =>
      prev.map((f) => (f.id === id ? { ...f, selected: !f.selected } : f)),
    );

  const remove = async (file: UploadedFile) => {
    if (file.status === "ready") {
      try {
        await deleteFile(file.id);
      } catch (err) {
        update(file.id, { error: (err as Error).message });
        return;
      }
    }
    onChange((prev) => prev.filter((f) => f.id !== file.id));
  };

  const onDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragging(false);
    addFiles(e.dataTransfer.files);
  };

  return (
    <section className={styles.panel} aria-label="Uploaded files">
      <header className={styles.header}>
        <div>
          <h2 className={styles.title}>Documents</h2>
          <p className={styles.subtitle}>
            {files.length} file{files.length === 1 ? "" : "s"} ·{" "}
            {files.filter((f) => f.selected).length} selected for chat
          </p>
        </div>
        <button
          type="button"
          className={styles.uploadButton}
          onClick={() => inputRef.current?.click()}
        >
          <UploadIcon width={16} height={16} />
          Upload
        </button>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED}
          multiple
          hidden
          onChange={(e) => {
            addFiles(e.target.files);
            e.target.value = "";
          }}
        />
      </header>

      {loadError && <p className={styles.banner}>{loadError}</p>}

      <div
        className={`${styles.body} ${dragging ? styles.dragging : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
      >
        {files.length === 0 ? (
          <button
            type="button"
            className={styles.empty}
            onClick={() => inputRef.current?.click()}
          >
            <UploadIcon width={28} height={28} />
            <span>Drop files here or click to upload</span>
            <span className={styles.hint}>PDF, DOCX, TXT, MD</span>
          </button>
        ) : (
          <ul className={styles.list}>
            {files.map((f) => (
              <li key={f.id} className={styles.row}>
                <input
                  type="checkbox"
                  checked={f.selected}
                  disabled={f.status !== "ready"}
                  onChange={() => toggle(f.id)}
                  aria-label={`Include ${f.name} in chat`}
                />
                <span className={styles.badge}>
                  {fileExtension(f.name) || "FILE"}
                </span>
                <div className={styles.meta}>
                  <span className={styles.name} title={f.name}>
                    {f.name}
                  </span>
                  <span className={styles.details}>
                    {formatBytes(f.size)} ·{" "}
                    <span
                      className={f.error ? styles.error : styles[f.status]}
                      title={f.error}
                    >
                      {f.error ??
                        (f.status === "uploading"
                          ? "Uploading & indexing…"
                          : "Ready")}
                    </span>
                  </span>
                </div>
                <button
                  type="button"
                  className={styles.remove}
                  onClick={() => remove(f)}
                  disabled={f.status === "uploading"}
                  aria-label={`Remove ${f.name}`}
                >
                  <TrashIcon width={16} height={16} />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
