"use client";

import { useCallback, useEffect, useState } from "react";
import Chat, { type ChatMessage, type Step } from "@/components/Chat";
import MapPanel from "@/components/MapPanel";
import { streamAgentChat, type Recommendation } from "@/lib/api";
import styles from "./page.module.css";

const USER_ID = "demo-user";

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [selectedCafeId, setSelectedCafeId] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  // Generated after mount so SSR and client agree (no hydration mismatch).
  const [sessionId, setSessionId] = useState<string | null>(null);
  useEffect(() => setSessionId(crypto.randomUUID()), []);

  // Update the in-flight assistant message (always the last one) immutably.
  const patchAssistant = useCallback(
    (fn: (m: Extract<ChatMessage, { role: "assistant" }>) => ChatMessage) => {
      setMessages((prev) => {
        const copy = prev.slice();
        const last = copy[copy.length - 1];
        if (last && last.role === "assistant") copy[copy.length - 1] = fn(last);
        return copy;
      });
    },
    []
  );

  const handleSend = useCallback(
    async (text: string) => {
      setBusy(true);
      setSelectedCafeId(null);
      setMessages((prev) => [
        ...prev,
        { role: "user", content: text },
        { role: "assistant", reply: "", steps: [], recommendations: [], streaming: true },
      ]);

      const addStep = (step: Step) =>
        patchAssistant((m) => ({ ...m, steps: [...m.steps, step] }));

      try {
        await streamAgentChat({
          sessionId: sessionId ?? crypto.randomUUID(),
          userId: USER_ID,
          message: text,
          onEvent: (ev) => {
            if (ev.event === "thought") {
              addStep({ kind: "thought", text: ev.data.text });
            } else if (ev.event === "action") {
              addStep({ kind: "action", text: `${ev.data.tool}(${JSON.stringify(ev.data.input)})` });
            } else if (ev.event === "observation") {
              addStep({ kind: "observation", text: `${ev.data.tool} → ${ev.data.output}` });
            } else if (ev.event === "final") {
              patchAssistant((m) => ({
                ...m,
                reply: ev.data.reply,
                recommendations: ev.data.recommendations,
                streaming: false,
              }));
              setRecommendations(ev.data.recommendations);
            }
          },
        });
      } catch (err) {
        patchAssistant((m) => ({
          ...m,
          reply: m.reply || `Sorry — something went wrong (${String(err)}).`,
          streaming: false,
        }));
      } finally {
        setBusy(false);
      }
    },
    [patchAssistant, sessionId]
  );

  return (
    <main className={styles.layout}>
      <div className={styles.chatCol}>
        <Chat
          messages={messages}
          onSend={handleSend}
          busy={busy}
          selectedCafeId={selectedCafeId}
          onSelectCafe={setSelectedCafeId}
        />
      </div>
      <div className={styles.mapCol}>
        <MapPanel
          recommendations={recommendations}
          selectedCafeId={selectedCafeId}
          onSelectCafe={setSelectedCafeId}
        />
      </div>
    </main>
  );
}
