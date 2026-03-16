export type TenantId = string;

export interface AuditMetadata {
  orgId: TenantId;
  action: string;
  actorId: string;
  timestamp: string;
}

export interface NodePolicy {
  nodeId: string;
  policyVersion: string;
  requireHumanApproval: boolean;
  maxCaseDocuments: number;
  telemetryMode: "redacted-only";
}
