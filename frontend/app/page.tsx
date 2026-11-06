"use client";

import { useEffect, useState } from "react";
import ChatPanel from "@/components/ChatPanel";
import FileList from "@/components/FileList";
import NavBar, { type NavSection } from "@/components/NavBar";
import { listFiles } from "@/lib/api";
import type { UploadedFile } from "@/lib/types";
import styles from "./page.module.css";

export default function Home() {
  const [section, setSection] = useState<NavSection>("chat");
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    listFiles()
      .then((serverFiles) =>
        setFiles(
          serverFiles.map((f) => ({
            id: f.id,
            name: f.name,
            size: f.size,
            uploadedAt: new Date(f.uploaded_at),
            status: "ready",
            selected: true,
          })),
        ),
      )
      .catch((err: Error) => setLoadError(err.message));
  }, []);

  return (
    <div className={styles.shell}>
      <NavBar active={section} onSelect={setSection} />
      <FileList files={files} onChange={setFiles} loadError={loadError} />
      <ChatPanel files={files} />
    </div>
  );
}
