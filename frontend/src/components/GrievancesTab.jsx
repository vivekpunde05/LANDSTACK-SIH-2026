import { useCallback, useEffect, useState } from 'react'
import { AlertCircle, CalendarDays, Camera, LoaderCircle, MessageSquareWarning, Plus } from 'lucide-react'
import GrievanceForm from './GrievanceForm'

export default function GrievancesTab({ parcel }) {
  const [items, setItems] = useState(null)
  const [error, setError] = useState('')
  const [formOpen, setFormOpen] = useState(false)
  const [expanded, setExpanded] = useState(null)
  const [lightbox, setLightbox] = useState(null)
  const load = useCallback(() => {
    setError('')
    fetch(`/api/parcels/${encodeURIComponent(parcel.parcel_id)}/grievances`)
      .then((response) => { if (!response.ok) throw new Error(); return response.json() })
      .then((data) => setItems(data.items))
      .catch(() => setError('Grievance history is unavailable. Ensure the local backend is running.'))
  }, [parcel.parcel_id])
  useEffect(load, [load])
  if (error) return <div className="space-y-3"><div className="flex gap-2 rounded-xl bg-rose-50 p-3 text-[10px] text-rose-800"><AlertCircle size={15} />{error}</div><button onClick={load} className="rounded-xl border border-ink/15 px-3 py-2 text-xs font-bold">Retry</button></div>
  if (!items) return <div className="grid min-h-52 place-items-center text-xs text-ink/50"><span className="flex items-center gap-2"><LoaderCircle size={15} className="animate-spin" /> Loading grievances…</span></div>
  const latest = items[0]
  return <div className="space-y-3">
    <div className="rounded-xl border border-blue-200 bg-blue-50 p-3 text-[10px] leading-relaxed text-blue-900">Citizen-submitted information requires official verification and does not constitute a legal determination.</div>
    <section className="rounded-xl bg-sand/65 p-3"><p className="text-[9px] font-extrabold uppercase tracking-widest text-moss">Parcel grievances · {items.length}</p>{latest ? <div className="mt-2"><p className="font-display text-sm font-extrabold">{latest.grievance_id}</p><p className="mt-1 text-xs font-bold">{latest.category}</p><div className="mt-2 flex flex-wrap gap-2 text-[9px] text-ink/55"><span>{latest.status}</span><span>·</span><span>{new Date(latest.submitted_at).toLocaleString()}</span><span>·</span><span>{latest.evidence_count} images</span></div></div> : <p className="mt-2 text-xs text-ink/55">No grievances have been recorded for this parcel.</p>}</section>
    <button onClick={() => setFormOpen(true)} className="flex w-full items-center justify-center gap-2 rounded-xl bg-ink px-4 py-3 text-xs font-bold text-white"><Plus size={15} /> Submit New Grievance</button>
    {items.map((item) => <article key={item.grievance_id} className="rounded-xl border border-ink/10 p-3"><div className="flex items-start justify-between gap-3"><div><p className="font-display text-xs font-extrabold">{item.grievance_id}</p><p className="mt-1 text-[10px] font-bold">{item.category}{item.custom_category ? ` — ${item.custom_category}` : ''}</p></div><span className="rounded-full bg-blue-100 px-2 py-1 text-[8px] font-extrabold text-blue-800">{item.status}</span></div><div className="mt-2 flex gap-3 text-[9px] text-ink/50"><span className="flex items-center gap-1"><CalendarDays size={11} />{new Date(item.submitted_at).toLocaleDateString()}</span><span className="flex items-center gap-1"><Camera size={11} />{item.evidence_count}</span></div><button onClick={() => setExpanded(expanded === item.grievance_id ? null : item.grievance_id)} className="mt-3 text-[10px] font-bold text-moss">{expanded === item.grievance_id ? 'Hide details' : 'View details'}</button>{expanded === item.grievance_id && <div className="mt-3 space-y-2 border-t border-ink/8 pt-3 text-[10px]"><p><strong>Description:</strong> {item.description}</p><p className="rounded-lg bg-amber-50 p-2 text-amber-900">{item.storage_notice}</p><p className="flex items-start gap-1 text-ink/55"><MessageSquareWarning size={12} className="mt-0.5 shrink-0" />Field verification may be recommended after administrative review.</p><div className="grid grid-cols-3 gap-2">{item.evidence.map((image) => <button key={image.evidence_id} onClick={() => setLightbox(image)}><img src={image.url} alt={image.file_name} className="aspect-square w-full rounded-lg object-cover" /></button>)}</div></div>}</article>)}
    {formOpen && <GrievanceForm parcel={parcel} completionLabel="Return to grievance history" onCompleted={load} onClose={() => { setFormOpen(false); load() }} />}
    {lightbox && <button onClick={() => setLightbox(null)} className="fixed inset-0 z-[80] grid place-items-center bg-black/85 p-4" aria-label="Close grievance evidence viewer"><img src={lightbox.url} alt={lightbox.file_name} className="max-h-[90vh] max-w-full rounded-xl object-contain" /></button>}
  </div>
}
