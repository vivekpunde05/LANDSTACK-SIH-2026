import { useEffect, useState } from 'react'
import { AlertCircle, CheckCircle2, Images, LoaderCircle, Play, ScanSearch } from 'lucide-react'

const statusTone = (status) => status === 'No significant change detected'
  ? 'bg-emerald-100 text-emerald-800'
  : status === 'Potential change' ? 'bg-amber-100 text-amber-900' : 'bg-rose-100 text-rose-800'

export default function SatelliteHistory({ parcel }) {
  const [imagery, setImagery] = useState(null)
  const [beforeDate, setBeforeDate] = useState('')
  const [afterDate, setAfterDate] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [view, setView] = useState('compare')

  useEffect(() => {
    const controller = new AbortController()
    setImagery(null); setResult(null); setError('')
    fetch(`/api/parcels/${encodeURIComponent(parcel.parcel_id)}/imagery`, { signal: controller.signal })
      .then((response) => { if (!response.ok) throw new Error('Imagery service unavailable'); return response.json() })
      .then((items) => {
        setImagery(items)
        if (items.length) { setBeforeDate(items[0].capture_date); setAfterDate(items[items.length - 1].capture_date) }
      })
      .catch((caught) => { if (caught.name !== 'AbortError') { setImagery([]); setError('Imagery service is currently unavailable.') } })
    return () => controller.abort()
  }, [parcel.parcel_id])

  const before = imagery?.find((item) => item.capture_date === beforeDate)
  const after = imagery?.find((item) => item.capture_date === afterDate)
  const runAnalysis = () => {
    setLoading(true); setError(''); setResult(null)
    fetch(`/api/parcels/${encodeURIComponent(parcel.parcel_id)}/change-analysis`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ before_date: beforeDate, after_date: afterDate }),
    }).then((response) => { if (!response.ok) throw new Error('Analysis could not be completed'); return response.json() })
      .then((data) => { setResult(data); setView('overlay'); setLoading(false) })
      .catch(() => { setError('Change analysis could not be completed. Check the selected imagery and backend service.'); setLoading(false) })
  }

  if (imagery === null) return <div className="grid min-h-56 place-items-center text-xs text-ink/55"><span className="flex items-center gap-2"><LoaderCircle size={16} className="animate-spin" /> Loading imagery history…</span></div>
  if (imagery.length === 0) return <div className="grid min-h-56 place-items-center rounded-xl border border-dashed border-ink/20 bg-sand/40 p-6 text-center"><div><Images size={26} className="mx-auto text-ink/35" /><p className="mt-3 text-sm font-bold">No imagery history is available for this synthetic demo parcel.</p>{error && <p className="mt-2 text-[10px] text-rose-700">{error}</p>}</div></div>

  return <div className="space-y-4">
    <div className="rounded-xl border border-blue-100 bg-blue-50 p-3 text-[10px] leading-relaxed text-blue-900"><strong>Demo imagery for prototype change-detection workflow.</strong> These images are synthetic and are not official satellite or cadastral evidence.</div>
    <div className="grid grid-cols-2 gap-2"><label className="text-[9px] font-bold uppercase tracking-wider text-ink/45">Before<select value={beforeDate} onChange={(event) => { setBeforeDate(event.target.value); setResult(null) }} className="mt-1 block h-9 w-full rounded-lg border border-ink/15 bg-white px-2 text-xs text-ink">{imagery.map((item) => <option key={item.id} value={item.capture_date}>{item.capture_date.slice(0, 4)}</option>)}</select></label><label className="text-[9px] font-bold uppercase tracking-wider text-ink/45">After<select value={afterDate} onChange={(event) => { setAfterDate(event.target.value); setResult(null) }} className="mt-1 block h-9 w-full rounded-lg border border-ink/15 bg-white px-2 text-xs text-ink">{imagery.map((item) => <option key={item.id} value={item.capture_date}>{item.capture_date.slice(0, 4)}</option>)}</select></label></div>
    {!result || view === 'compare' ? <div className="grid grid-cols-2 gap-2">{[[before, 'Before'], [after, 'After']].map(([item, label]) => <figure key={label} className="overflow-hidden rounded-xl border border-ink/10 bg-sand"><img src={item?.image_url} alt={`${label} synthetic demo imagery`} className="aspect-[4/3] w-full object-cover" /><figcaption className="flex items-center justify-between px-2 py-2 text-[9px]"><strong>{label.toUpperCase()}</strong><span>{item?.capture_date.slice(0, 4)}</span></figcaption></figure>)}</div> : <figure className="overflow-hidden rounded-xl border border-ink/10 bg-sand"><img src={view === 'overlay' ? result.overlay_url : result.mask_url} alt={`${view} change detection result`} className="aspect-[4/3] w-full object-cover" /><figcaption className="px-3 py-2 text-[9px] font-bold uppercase tracking-wider">{view === 'overlay' ? 'Change overlay' : 'Binary change mask'}</figcaption></figure>}
    {result && <div className="flex rounded-xl bg-sand p-1">{[['compare', 'Before / After'], ['overlay', 'Overlay'], ['mask', 'Mask']].map(([key, label]) => <button key={key} onClick={() => setView(key)} className={`flex-1 rounded-lg px-2 py-2 text-[9px] font-bold ${view === key ? 'bg-white text-moss shadow-sm' : 'text-ink/45'}`}>{label}</button>)}</div>}
    <button disabled={loading || !before || !after || beforeDate >= afterDate} onClick={runAnalysis} className="flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-ink text-xs font-bold text-white transition hover:bg-moss disabled:cursor-not-allowed disabled:opacity-45">{loading ? <><LoaderCircle size={16} className="animate-spin" /> Running change detection…</> : <><Play size={15} /> Run Change Detection</>}</button>
    {error && <div className="flex gap-2 rounded-xl bg-rose-50 p-3 text-[10px] text-rose-800"><AlertCircle size={15} className="shrink-0" />{error}</div>}
    {result && <section className="space-y-3 rounded-xl border border-ink/10 p-3"><div className="flex items-center justify-between"><p className="text-[10px] font-extrabold uppercase tracking-widest text-moss">Change detection result</p><span className={`rounded-full px-2 py-1 text-[9px] font-bold ${statusTone(result.change_status)}`}>{result.change_status}</span></div><div className="grid grid-cols-2 gap-2"><div className="rounded-lg bg-sand p-2"><p className="text-[9px] uppercase text-ink/40">Changed area</p><p className="text-sm font-extrabold">{result.changed_area_sqm} m²</p></div><div className="rounded-lg bg-sand p-2"><p className="text-[9px] uppercase text-ink/40">Parcel change</p><p className="text-sm font-extrabold">{result.change_percentage}%</p></div></div><div className="rounded-lg bg-sand/60 p-3"><p className="flex items-center gap-2 text-[10px] font-extrabold"><ScanSearch size={15} /> Why was this parcel flagged?</p><dl className="mt-2 space-y-1 text-[10px] leading-relaxed"><div><dt className="inline font-bold">Main region: </dt><dd className="inline">{result.main_changed_region}</dd></div><div><dt className="inline font-bold">Analysis: </dt><dd className="inline">{result.analysis_explanation}</dd></div><div><dt className="inline font-bold">Recommendation: </dt><dd className="inline">{result.recommendation}</dd></div></dl></div><p className="flex gap-2 text-[9px] leading-relaxed text-ink/55"><CheckCircle2 size={14} className="shrink-0 text-moss" />{result.legal_notice}</p></section>}
  </div>
}
