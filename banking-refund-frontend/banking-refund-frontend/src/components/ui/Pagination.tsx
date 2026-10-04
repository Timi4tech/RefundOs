import { ChevronLeft, ChevronRight } from "lucide-react";

export function Pagination({
  page, totalPages, onChange
}: { page: number; totalPages: number; onChange: (page: number) => void }) {
  if (totalPages <= 1) return null;
  return (
    <div className="flex items-center justify-between border-t border-slateText-100 px-4 py-3">
      <p className="text-xs text-slateText-500">Page {page} of {totalPages}</p>
      <div className="flex gap-2">
        <button className="btn-secondary px-3 py-2" disabled={page <= 1} onClick={() => onChange(page - 1)}>
          <ChevronLeft size={16} /> Previous
        </button>
        <button className="btn-secondary px-3 py-2" disabled={page >= totalPages} onClick={() => onChange(page + 1)}>
          Next <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}
