export interface SkillManifest {
  id: string;
  version: string;
  requiresEntitlement: boolean;
  executionPolicy: {
    requiresHumanApproval: boolean;
    deterministicOutput: boolean;
  };
  packageChecksum: string;
  signature: string;
}

export function validateManifest(manifest: SkillManifest): boolean {
  return Boolean(
    manifest.id &&
      manifest.version &&
      manifest.packageChecksum &&
      manifest.signature &&
      typeof manifest.executionPolicy?.requiresHumanApproval === "boolean" &&
      typeof manifest.executionPolicy?.deterministicOutput === "boolean"
  );
}
