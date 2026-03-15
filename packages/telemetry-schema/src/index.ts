export interface RedactedTelemetryEvent {
  orgId: string;
  nodeId: string;
  metric: string;
  value: number;
  redactionLevel: "strict";
  capturedAt: string;
}

export interface RedactedTelemetryBatch {
  nodeId: string;
  metrics: Record<string, number>;
  redactionLevel: "strict";
}
