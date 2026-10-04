import type { RefundStatus } from "../../types";

const styles: Record<RefundStatus, string> = {
  PENDING: "bg-amber-50 text-amber-700",
  PROCESSING: "bg-blue-50 text-blue-700",
  APPROVED: "bg-emerald-50 text-emerald-700",
  REJECTED: "bg-red-50 text-red-700",
  REQUIRES_REVIEW: "bg-violet-50 text-violet-700",
  COMPLETED: "bg-teal/10 text-teal",
  FAILED: "bg-slate-100 text-slate-600"
};

export function StatusBadge({ status }: { status: RefundStatus }) {
  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-[11px] font-bold uppercase tracking-wide ${styles[status]}`}>
      {status.replaceAll("_", " ")}
    </span>
  );
}
