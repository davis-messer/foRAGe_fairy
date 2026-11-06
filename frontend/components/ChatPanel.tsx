"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { sendChatMessage } from "@/lib/api";
import type { ChatMessage, UploadedFile } from "@/lib/types";
import { SendIcon } from "./Icons";
import styles from "./ChatPanel.module.css";

interface ChatPanelProps {
  files: UploadedFile[];
}

export default function ChatPanel({ files }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  const contextFiles = files.filter((f) => f.selected && f.status === "ready");

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, pending]);

  const submit = async (e?: FormEvent) => {
    e?.preventDefault();
    const question = input.trim();
    if (!question || pending) return;

    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", content: question, createdAt: new Date() },
    ]);
    setInput("");
    setPending(true);

    try {
      const { answer, sources } = await sendChatMessage(
        question,
        contextFiles.map((f) => f.id),
      );
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: answer,
          sources,
          createdAt: new Date(),
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: (err as Error).message,
          error: true,
          createdAt: new Date(),
        },
      ]);
    } finally {
      setPending(false);
    }
  };

  return (
    <section className={styles.panel} aria-label="Chat">
      <header className={styles.header}>
        <h2 className={styles.title}>Chat</h2>
        <p className={styles.subtitle}>
          {contextFiles.length > 0
            ? `Answering from ${contextFiles.length} document${contextFiles.length === 1 ? "" : "s"}`
            : "No documents selected"}
        </p>
      </header>

      <div className={styles.messages}>
        {messages.length === 0 && !pending ? (
          <div className={styles.empty}>
            <h3>Ask about your documents</h3>
            <p>Upload files on the left, then ask a question here.</p>
          </div>
        ) : (
          messages.map((m) => (
            <div
              key={m.id}
              className={`${styles.message} ${m.role === "user" ? styles.user : styles.assistant} ${m.error ? styles.error : ""}`}
            >
              {m.content}
              {m.sources && m.sources.length > 0 && (
                <div className={styles.sources}>
                  {m.sources.map((s) => (
                    <span key={s} className={styles.source}>
                      {s}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
        {pending && (
          <div className={`${styles.message} ${styles.assistant} ${styles.typing}`}>
            <span />
            <span />
            <span />
          </div>
        )}
        <div ref={endRef} />
      </div>

      <form className={styles.composer} onSubmit={submit}>
        <textarea
          className={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          placeholder="Ask a question about your documents…"
          rows={1}
          aria-label="Message"
        />
        <button
          type="submit"
          className={styles.send}
          disabled={!input.trim() || pending}
          aria-label="Send"
        >
          <SendIcon width={18} height={18} />
        </button>
      </form>
    </section>
  );
}
