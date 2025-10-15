import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LiveLogView, LiveEvent } from "./LiveLogView";

class StubSocket {
  constructor(private events: LiveEvent[]) {}
  subscribe(callback: (data: unknown) => void) {
    this.events.forEach((event) => callback(event));
    return () => undefined;
  }
}

describe("LiveLogView", () => {
  const baseEvent: LiveEvent = {
    kind: "iec104.frame",
    role: "client",
    dir: "tx",
    ts: new Date().toISOString(),
    apci: { type: "I", vs: -1, vr: -1 },
    asdu: { typeId: 45, cause: 6, ca: 1, ioa: 1, payload: { value: true } },
    raw: null,
  };

  it("renders incoming events", () => {
    render(<LiveLogView socket={new StubSocket([baseEvent]) as never} />);
    expect(screen.getByText(/CLIENT TX Type 45/i)).toBeInTheDocument();
  });

  it("filters by direction", () => {
    const events = [
      baseEvent,
      { ...baseEvent, dir: "rx", asdu: { ...baseEvent.asdu, typeId: 1 } },
    ];
    render(<LiveLogView socket={new StubSocket(events) as never} />);
    const selects = screen.getAllByRole("combobox");
    const dirSelect = selects[1] as HTMLSelectElement;
    dirSelect.value = "rx";
    dirSelect.dispatchEvent(new Event("change", { bubbles: true }));
    expect(screen.getByText(/CLIENT RX Type 1/)).toBeInTheDocument();
  });
});
