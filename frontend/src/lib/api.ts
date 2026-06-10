// Client for the CoffeeCompass agent's streaming endpoint.
//
// /agent/chat is a POST that returns Server-Sent Events. Native EventSource only
// does GET and can't send a JSON body, so we consume the SSE stream with fetch +
// a ReadableStream reader and parse the frames ourselves.

export type Recommendation = {
  id: number;
  name: string;
  lat: number;
  lng: number;
  price_level: number | null;
  has_outlet: boolean | null;
  noise_level: string | null;
  ambience_text: string | null;
  open_now: boolean | null;
};

export type AgentEvent =
  | { event: "thought"; data: { text: string } }
  | { event: "action"; data: { tool: string; input: unknown } }
  | { event: "observation"; data: { tool: string; output: string } }
  | { event: "final"; data: { reply: string; recommendations: Recommendation[] } };

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

function parseFrame(frame: string): AgentEvent | null {
  let event = "";
  let data = "";
  for (const line of frame.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) data += line.slice(5).trim();
  }
  if (!event || !data) return null;
  try {
    return { event, data: JSON.parse(data) } as AgentEvent;
  } catch {
    return null;
  }
}

export async function streamAgentChat(params: {
  sessionId: string;
  userId: string;
  message: string;
  onEvent: (ev: AgentEvent) => void;
  signal?: AbortSignal;
}): Promise<void> {
  const res = await fetch(`${API_BASE}/agent/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: params.sessionId,
      user_id: params.userId,
      message: params.message,
    }),
    signal: params.signal,
  });
  if (!res.ok || !res.body) {
    throw new Error(`agent/chat failed: ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    // Normalise CRLF so frame boundaries are always "\n\n".
    buffer = (buffer + decoder.decode(value, { stream: true })).replace(/\r\n/g, "\n");
    let idx: number;
    while ((idx = buffer.indexOf("\n\n")) !== -1) {
      const frame = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      const ev = parseFrame(frame);
      if (ev) params.onEvent(ev);
    }
  }
}
