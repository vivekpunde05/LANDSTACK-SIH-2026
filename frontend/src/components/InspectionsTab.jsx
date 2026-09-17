import { useCallback, useEffect, useState } from 'react'
import { AlertCircle, CalendarDays, Camera, CheckCircle2, LoaderCircle, MapPin, Plus } from 'lucide-react'
import InspectionForm from './InspectionForm'

export default function InspectionsTab({ parcel }) {
  const [items, setItems] = useState(null)
  const [error, setError] = useState('')
  const [formOpen, setFormOpen] = useState(false)
  const [expanded, setExpanded] = useState(null)
  const [lightbox, setLightbox] = useState(null)
  const load = useCallback(() => {
    setError('')
    fetch(`/api/parcels/${encodeURIComponent(parcel.parcel_id)}/inspections`)
      .then((response) => { if (!response.ok) throw new Error(); return response.json() })
      .then((data) => setItems(data.items))
      .catch(() => setError('Inspection history is unavailable. Ensure the local backend is running.'))
  }, [parcel.parcel_id])
  useEffect(load, [load])

  if (error) return <div className="space-y-3"><div className="flex gap-2 rounded-xl bg-rose-50 p-3 text-[10px] text-rose-800"><AlertCircle size={15} />{error}</div><button onClick={load} className="rounded-xl border border-ink/15 px-3 py-2 text-xs font-bold">Retry</button></div>
  if (!items) return <div className="grid min-h-52 place-items-center text-xs text-ink/50"><span className="flex items-center gap-2"><LoaderCircle size={15} className="animate-spin" /> Loading inspections…</span></div>
  const latest = items[0]
  return <div className="space-y-3">
    <section className="rounded-xl bg-sand/65 p-3"><p className="text-[9px] font-extrabold uppercase tracking-widest text-moss">Latest inspection status</p>{latest ? <div className="mt-2"><p className="text-sm font-extrabold">{latest.inspection_status}</p><p className="mt-1 text-xs">{latest.inspection_outcome}</p><div className="mt-2 flex flex-wrap gap-2 text-[9px] text-ink/55"><span>{new Date(latest.completed_at).toLocaleString()}</span><span>·</span><span>{latest.location ? 'Location recorded' : 'No location'}</span><span>·</span><span>{latest.evidence_count} photos</span><span>·</span><span>{latest.requires_follow_up ? 'Follow-up required' : 'No follow-up'}</span></div></div> : <p className="mt-2 text-xs text-ink/55">No inspections have been recorded for this parcel.</p>}</section>
    <button onClick={() => setFormOpen(true)} className="flex w-full items-center justify-center gap-2 rounded-xl bg-ink px-4 py-3 text-xs font-bold text-white"><Plus size={15} /> Start New Inspection</button>
    {items.map((item, index) => <article key={item.inspection_id} className="rounded-xl border border-ink/10 p-3"><div className="flex items-start justify-between gap-3"><div><p className="text-[9px] font-bold uppercase tracking-wider text-ink/40">Inspection #{items.length - index}</p><p className="mt-1 text-xs font-extrabold">{item.inspection_outcome}</p></div><CheckCircle2 size={18} className="text-emerald-600" /></div><div className="mt-2 flex gap-3 text-[9px] text-ink/50"><span className="flex items-center gap-1"><CalendarDays size={11} />{new Date(item.completed_at).toLocaleDateString()}</span><span className="flex items-center gap-1"><Camera size={11} />{item.evidence_count}</span><span className="flex items-center gap-1"><MapPin size={11} />{item.location ? 'Available' : 'Unavailable'}</span></div><button onClick={() => setExpanded(expanded === item.inspection_id ? null : item.inspection_id)} className="mt-3 text-[10px] font-bold text-moss">{expanded === item.inspection_id ? 'Hide details' : 'View details'}</button>{expanded === item.inspection_id && <div className="mt-3 space-y-2 border-t border-ink/8 pt-3 text-[10px]"><p><strong>Observations:</strong> {item.observations}</p><p><strong>Follow-up:</strong> {item.requires_follow_up ? `Yes${item.recommendation ? ` — ${item.recommendation}` : ''}` : 'No'}</p><p className="rounded-lg bg-amber-50 p-2 text-amber-900">{item.storage_notice}</p><div className="grid grid-cols-3 gap-2">{item.evidence.map((photo) => <button key={photo.evidence_id} onClick={() => setLightbox(photo)}><img src={photo.url} alt={photo.file_name} className="aspect-square w-full rounded-lg object-cover" /></button>)}</div></div>}</article>)}
    {formOpen && <InspectionForm parcel={parcel} completionLabel="Return to inspection history" onCompleted={() => load()} onClose={() => { setFormOpen(false); load() }} />}
    {lightbox && <button onClick={() => setLightbox(null)} className="fixed inset-0 z-[80] grid place-items-center bg-black/85 p-4" aria-label="Close evidence viewer"><img src={lightbox.url} alt={lightbox.file_name} className="max-h-[90vh] max-w-full rounded-xl object-contain" /></button>}
  </div>
}
