import { useEffect, useState } from 'react'
import { AlertCircle, CheckCircle2, LoaderCircle, ShieldCheck } from 'lucide-react'

const levelTone = {
  Routine: 'bg-emerald-100 text-emerald-800',
  'Review Recommended': 'bg-amber-100 text-amber-900',
  'High Priority Review': 'bg-orange-100 text-orange-900',
  'Urgent Review': 'bg-rose-100 text-rose-900',
}

export default function PriorityTab({ parcel }) {
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => {
    const controller = new AbortController()
    setResult(null); setError('')
    fetch(`/api/parcels/${encodeURIComponent(parcel.parcel_id)}/priority`, { signal: controller.signal })
      .then((response) => { if (!response.ok) throw new Error('Priority service unavailable'); return response.json() })
      .then(setResult)
      .catch((caught) => { if (caught.name !== 'AbortError') setError('Inspection priority could not be calculated. Ensure the backend service is running.') })
    return () => controller.abort()
  }, [parcel.parcel_id])

  if (error) return <div className="flex gap-2 rounded-xl bg-rose-50 p-4 text-[10px] text-rose-800"><AlertCircle size={16} className="shrink-0" />{error}</div>
  if (!result) return <div className="grid min-h-56 place-items-center text-xs text-ink/55"><span className="flex items-center gap-2"><LoaderCircle size={16} className="animate-spin" /> Calculating inspection priority…</span></div>

  return <div className="space-y-4">
    <section className="rounded-2xl bg-ink p-4 text-white">
      <div className="flex items-center justify-between gap-4"><div><p className="text-[9px] font-extrabold uppercase tracking-[.18em] text-lime">Inspection Priority</p><p className="mt-1 font-display text-4xl font-extrabold">{result.priority_score}<span className="text-base text-white/45"> / 100</span></p></div><ShieldCheck size={34} className="text-lime" /></div>
      <span className={`mt-3 inline-flex rounded-full px-2.5 py-1 text-[9px] font-extrabold ${levelTone[result.priority_level]}`}>{result.priority_level}</span>
    </section>
    <section><p className="mb-2 text-[10px] font-extrabold uppercase tracking-widest text-moss">Why this score?</p><div className="space-y-2">{result.factors.map((factor) => <div key={factor.factor} className="rounded-xl border border-ink/10 p-3"><div className="flex justify-between text-[10px] font-bold"><span>{factor.factor}</span><span>{factor.points} / {factor.max_points}</span></div><div className="mt-2 h-1.5 overflow-hidden rounded-full bg-sand"><div className="h-full rounded-full bg-moss" style={{ width: `${factor.max_points ? factor.points / factor.max_points * 100 : 0}%` }} /></div><p className="mt-2 text-[9px] leading-relaxed text-ink/50">{factor.reason}</p></div>)}</div></section>
    <div className="rounded-xl border border-lime/60 bg-lime/15 p-3"><p className="text-[9px] font-bold uppercase tracking-wider text-ink/45">Recommendation</p><p className="mt-1 text-xs font-bold">{result.recommendation}</p></div>
    <div className="rounded-xl bg-sand/65 p-3 text-[9px] leading-relaxed text-ink/55"><div className="flex items-center gap-2 font-bold text-ink"><CheckCircle2 size={14} /> Score version: {result.score_version}</div><p className="mt-1">Calculated: {new Date(result.calculated_at).toLocaleString()}</p><p className="mt-2">{result.threshold_notice}</p><p className="mt-1">Database: {result.persistence}</p></div>
  </div>
}
