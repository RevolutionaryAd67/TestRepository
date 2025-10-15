export interface RequestOptions<TBody> {
  method?: "GET" | "POST" | "PUT";
  body?: TBody;
  headers?: Record<string, string>;
}

const BASE_URL = "http://localhost:8000";

export async function apiRequest<TResponse, TBody = unknown>(
  path: string,
  options: RequestOptions<TBody> = {}
): Promise<TResponse> {
  const { method = "GET", body, headers } = options;
  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  if (response.status === 204) {
    return undefined as TResponse;
  }
  return (await response.json()) as TResponse;
}

export class LiveSocket {
  private socket: WebSocket | null = null;
  private shouldReconnect = true;
  private readonly listeners = new Set<(data: unknown) => void>();

  constructor(private readonly url = "ws://localhost:8000/ws/live") {
    this.open();
  }

  private open() {
    if (typeof WebSocket === 'undefined') {
      return;
    }
    this.socket = new WebSocket(this.url);
    this.socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        this.listeners.forEach((listener) => listener(payload));
      } catch (error) {
        console.error("Failed to parse websocket event", error);
      }
    };
    this.socket.onclose = () => {
      if (this.shouldReconnect) {
        setTimeout(() => this.open(), 1000);
      }
    };
  }

  public subscribe(listener: (data: unknown) => void) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  public close() {
    this.shouldReconnect = false;
    this.socket?.close();
    this.listeners.clear();
  }
}
