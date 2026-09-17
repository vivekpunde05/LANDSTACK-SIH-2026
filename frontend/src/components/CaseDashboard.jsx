import { useCallback, useEffect, useMemo, useState } from 'react'
import { AlertCircle, Eye, LoaderCircle, RotateCcw, ShieldCheck } from 'lucide-react'
import { caseStatuses, priorityLevels, reviewStages } from '../data/caseOptions'

const emptyFilters = { status: '', stage: '', taluka: '', priority: '' }
const summaryStatuses = ['Open', 'Under Review', 'Field Verification Requested', 'More Information Required', 'Ready for Decision', 'Resolved']

export default function CaseDashboard({ onViewCase }) {
  const [items, setItems] = useState(null)
  const [error, setError] = useState('')
  const [filters, setFilters] = useState(emptyFilters)
  const load = useCallback(() => {
    setError('')
    fetch('/api/cases?limit=100')
      .then((response) => response.ok ? response.json() : Promise.reject())
      .then((data) => setItems(data.items))
      .catch(() => setError('Administrative case queue is unavailable. Ensure the local backend is running.'))
  }, [])
  useEffect(() => { load() }, [load])
  const visible = useMemo(() => (items || []).filter((item) =>
    (!filters.status || item.case_status === filters.status) &&
    (!filters.stage || item.review_stage === filters.stage) &&
    (!filters.taluka || item.taluka === filters.taluka) &&
    (!filters.priority || item.latest_priority_level === filters.priority),
  ), [items, filters])
  const counts = useMemo(() => Object.fromEntries(summaryStatuses.map((status) => [status, (items || []).filter((item) => item.case_status === status).length])), [items])
  return <div className="space-y-4">
    <div className="flex items-center justify-between rounded-2xl border border-violet-200 bg-violet-50 p-4 text-violet-950"><div><p className="text-[9px] font-extrabold uppercase tracking-widest">Demo Administrative Session</p><p className="mt-1 text-xs font-bold">Admin Officer · DEMO-ADMIN-01</p></div><ShieldCheck size={22} /></div>
    <div className="grid grid-cols-2 gap-2 md:grid-cols-3 xl:grid-cols-6">{summaryStatuses.map((status) => <div key={status} className="rounded-2xl border border-ink/10 bg-white p-3"><p className="font-display text-xl font-extrabold">{items ? counts[status] : '…'}</p><p className="text-[8px] font-bold uppercase tracking-wider text-ink/45">{status}</p></div>)}</div>
    <section className="rounded-2xl border border-ink/10 bg-white p-4"><div className="flex items-center justify-between"><div><p className="text-[9px] font-extrabold uppercase tracking-widest text-moss">Workflow queue</p><h3 className="font-display text-lg font-extrabold">Administrative Case Queue</h3></div><button onClick={() => setFilters(emptyFilters)} className="flex items-center gap-1 text-[10px] font-bold text-moss"><RotateCcw size={13} /> Clear filters</button></div><div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-4"><select aria-label="Case status filter" value={filters.status} onChange={(event) => setFilters((value) => ({ ...value, status: event.target.value }))} className="h-10 rounded-xl border px-3 text-xs"><option value="">All case statuses</option>{caseStatuses.map((value) => <option key={value}>{value}</option>)}</select><select aria-label="Review stage filter" value={filters.stage} onChange={(event) => setFilters((value) => ({ ...value, stage: event.target.value }))} className="h-10 rounded-xl border px-3 text-xs"><option value="">All review stages</option>{reviewStages.map((value) => <option key={value}>{value}</option>)}</select><select aria-label="Case taluka filter" value={filters.taluka} onChange={(event) => setFilters((value) => ({ ...value, taluka: event.target.value }))} className="h-10 rounded-xl border px-3 text-xs"><option value="">All talukas</option>{['Ratnagiri', 'Chiplun', 'Sangameshwar'].map((value) => <option key={value}>{value}</option>)}</select><select aria-label="Case priority filter" value={filters.priority} onChange={(event) => setFilters((value) => ({ ...value, priority: event.target.value }))} className="h-10 rounded-xl border px-3 text-xs"><option value="">All priority levels</option>{priorityLevels.map((value) => <option key={value}>{value}</option>)}</select></div></section>
    {error ? <div className="flex items-center justify-between gap-3 rounded-xl bg-rose-50 p-4 text-xs text-rose-800"><span className="flex items-center gap-2"><AlertCircle size={15} />{error}</span><button onClick={load} className="rounded-lg border border-rose-300 px-3 py-2 font-bold">Retry</button></div> : !items ? <div className="grid min-h-48 place-items-center rounded-2xl bg-white text-xs text-ink/50"><span className="flex items-center gap-2"><LoaderCircle size={16} className="animate-spin" /> Loading administrative cases…</span></div> : <section className="overflow-hidden rounded-2xl border border-ink/10 bg-white"><div className="border-b px-4 py-3 text-[10px] text-ink/50">Most recently updated first · {visible.length} cases</div><div className="overflow-x-auto"><table className="w-full min-w-[900px] text-left text-xs"><thead className="bg-sand/70 text-[9px] uppercase tracking-wider text-ink/45"><tr>{['Case ID', 'Grievance ID', 'Parcel', 'Village', 'Status', 'Review Stage', 'Priority', 'Updated', 'Action'].map((value) => <th key={value} className="px-3 py-3">{value}</th>)}</tr></thead><tbody className="divide-y divide-ink/8">{visible.map((item) => <tr key={item.case_id}><td className="px-3 py-3 font-bold">{item.case_id}</td><td className="px-3 py-3">{item.grievance_id}</td><td className="px-3 py-3">{item.parcel_id}</td><td className="px-3 py-3">{item.village}</td><td className="px-3 py-3"><span className="rounded-full bg-violet-100 px-2 py-1 text-[9px] font-bold text-violet-900">{item.case_status}</span></td><td className="px-3 py-3">{item.review_stage}</td><td className="px-3 py-3">{item.latest_priority_score} · {item.latest_priority_level}</td><td className="px-3 py-3">{new Date(item.updated_at).toLocaleDateString()}</td><td className="px-3 py-3"><button onClick={() => onViewCase(item.case_id)} className="flex items-center gap-1 rounded-lg bg-ink px-3 py-2 text-[10px] font-bold text-white"><Eye size={12} /> View Case</button></td></tr>)}</tbody></table>{visible.length === 0 && <p className="p-8 text-center text-xs text-ink/50">No administrative cases match the current filters.</p>}</div></section>}
    <p className="rounded-xl bg-amber-50 p-3 text-[10px] text-amber-900">Administrative outcomes are human review records for this demonstration workflow and do not establish legal ownership, wrongdoing, or enforcement action.</p>
  </div>
}
