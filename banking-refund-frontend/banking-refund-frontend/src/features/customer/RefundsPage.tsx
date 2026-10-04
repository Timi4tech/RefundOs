import { useEffect, useState } from "react";
import { Search, Plus, RefreshCw } from "lucide-react";
import api from "../../lib/api";
import type { Paginated, Refund } from "../../types";
import { StatusBadge } from "../../components/ui/StatusBadge";
import { Pagination } from "../../components/ui/Pagination";
import { ChatWidget } from "../../components/chat/ChatWidget";

export function RefundsPage() {
  const [data, setData] = useState<Paginated<Refund>>({ items: [], total: 0, page: 1, page_size: 10, total_pages: 1 });
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const res = await api.get("/refunds", { params: { page, page_size: 10 } });
      setData(res.data);
    } finally { setLoading(false); }
  }

  useEffect(() => { load(); }, [page]);

  return (
    <div className="mx-auto max-w-7xl">
      <div className="mb-7 flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div><p className="text-sm font-semibold text-teal">Customer portal</p><h2 className="mt-1 text-3xl font-bold tracking-tight">Refund requests</h2><p className="mt-2 text-sm text-slate-500">Review the status and history of your requests.</p></div>
        <button className="btn-primary"><Plus size={17}/> New refund</button>
      </div>
      <div className="panel overflow-hidden">
        <div className="flex items-center justify-between border-b border-slateText-100 p-4"><div className="relative w-full max-w-sm"><Search className="absolute left-3 top-3 text-slate-400" size={17}/><input className="input pl-10" placeholder="Search your refunds"/></div><button onClick={load} className="btn-secondary ml-3 px-3"><RefreshCw size={16}/></button></div>
        {loading ? <div className="p-10 text-center text-sm text-slateText-400">Loading refunds…</div> : data.items.length === 0 ? <div className="p-10 text-center text-sm text-slateText-400">No refund requests yet.</div> :
          <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="bg-slate-50 text-xs uppercase text-slateText-500"><tr><th className="px-5 py-3">Ticket</th><th className="px-5 py-3">Amount</th><th className="px-5 py-3">Status</th><th className="px-5 py-3">Created</th></tr></thead><tbody>{data.items.map(r => <tr key={r.id} className="border-t border-slateText-100"><td className="px-5 py-4 font-semibold">{r.id.slice(0, 12)}…</td><td className="px-5 py-4">{r.currency} {Number(r.amount).toLocaleString()}</td><td className="px-5 py-4"><StatusBadge status={r.status}/></td><td className="px-5 py-4 text-slateText-500">{new Date(r.created_at).toLocaleString()}</td></tr>)}</tbody></table></div>}
        <Pagination page={data.page} totalPages={data.total_pages} onChange={setPage}/>
      </div>
      <ChatWidget />
    </div>
  );
}
