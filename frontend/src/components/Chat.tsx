"use client";

import { useState } from "react";
import type { Recommendation } from "@/lib/api";
import styles from "./Chat.module.css";

export type Step = {
  kind: "thought" | "action" | "observation";
  text: string;
};

export type ChatMessage =
  | { role: "user"; content: string }
  | {
      role: "assistant";
      reply: string;
      steps: Step[];
      recommendations: Recommendation[];
      streaming: boolean;
    };

function ReasoningSteps({ steps }: { steps: Step[] }) {
  const [open, setOpen] = useState(false);
  if (steps.length === 0) return null;
  return (
    <details className={styles.reasoning} open={open} onToggle={(e) => setOpen(e.currentTarget.open)}>
      <summary>{open ? "Hide" : "Show"} reasoning ({steps.length} steps)</summary>
      <ol className={styles.steps}>
        {steps.map((s, i) => (
          <li key={i} className={styles[s.kind]}>
            <span className={styles.stepKind}>{s.kind}</span>
            <span className={styles.stepText}>{s.text}</span>
          </li>
        ))}
      </ol>
    </details>
  );
}

function RecommendationChips({
  recs,
  selectedId,
  onSelect,
}: {
  recs: Recommendation[];
  selectedId: number | null;
  onSelect: (id: number | null) => void;
}) {
  if (recs.length === 0) return null;
  return (
    <div className={styles.recs}>
      {recs.map((r) => (
        <button
          key={r.id}
          type="button"
          className={`${styles.recChip} ${selectedId === r.id ? styles.recChipActive : ""}`}
          onMouseEnter={() => onSelect(r.id)}
          onClick={() => onSelect(r.id)}
        >
          <span className={styles.recName}>{r.name}</span>
          {r.price_level != null && <span className={styles.recMeta}>{"$".repeat(r.price_level)}</span>}
          {r.open_now && <span className={styles.recOpen}>open</span>}
        </button>
      ))}
    </div>
  );
}

export default function Chat({
  messages,
  onSend,
  busy,
  selectedCafeId,
  onSelectCafe,
}: {
  messages: ChatMessage[];
  onSend: (text: string) => void;
  busy: boolean;
  selectedCafeId: number | null;
  onSelectCafe: (id: number | null) => void;
}) {
  const [input, setInput] = useState("");

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || busy) return;
    setInput("");
    onSend(text);
  }

  return (
    <section className={styles.chat}>
      <header className={styles.header}>
        <h1>CoffeeCompass</h1>
        <p>Ask for a coffee spot near USC — try a follow-up like &ldquo;anything cheaper?&rdquo;</p>
      </header>

      <div className={styles.messages}>
        {messages.length === 0 && (
          <p className={styles.empty}>e.g. &ldquo;a quiet place to study with outlets&rdquo;</p>
        )}
        {messages.map((m, i) =>
          m.role === "user" ? (
            <div key={i} className={`${styles.bubble} ${styles.user}`}>
              {m.content}
            </div>
          ) : (
            <div key={i} className={`${styles.bubble} ${styles.assistant}`}>
              <ReasoningSteps steps={m.steps} />
              <div className={styles.reply}>
                {m.reply || (m.streaming ? <span className={styles.typing}>…</span> : "")}
              </div>
              <RecommendationChips
                recs={m.recommendations}
                selectedId={selectedCafeId}
                onSelect={onSelectCafe}
              />
            </div>
          )
        )}
      </div>

      <form className={styles.inputRow} onSubmit={submit}>
        <input
          className={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about a coffee spot…"
          disabled={busy}
        />
        <button className={styles.send} type="submit" disabled={busy || !input.trim()}>
          {busy ? "…" : "Send"}
        </button>
      </form>
    </section>
  );
}
