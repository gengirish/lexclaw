export interface PolicyContext {
  role: "owner" | "admin" | "operator";
  action: string;
}

export function allowAction(context: PolicyContext): boolean {
  if (context.role === "owner") return true;
  if (context.role === "admin") return context.action !== "org:delete";
  return context.action.startsWith("read:");
}
