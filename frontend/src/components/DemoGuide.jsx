import { useEffect, useRef } from 'react'
import { BarChart3, ClipboardList, FileDown, Map, MessageSquareWarning, Satellite, ShieldCheck, X } from 'lucide-react'

const steps = [
  { id: 'gis', icon: Map, title: 'GIS Intelligence', detail: 'Open RTN-CHI-0013 and review its synthetic parcel record.' },
  { id: 'satellite', icon: Satellite, title: 'Satellite Analysis', detail: 'Compare 2023/2026 imagery and run explainable change detection.' },
  { id: 'priority', icon: ClipboardList, title: 'Inspection Priority', detail: 'Review the deterministic score and its contributing factors.' },
  { id: 'grievance', icon: MessageSquareWarning, title: 'Citizen Governance', detail: 'Review or submit a parcel-linked citizen concern.' },
  { id: 'cases', icon: ShieldCheck, title: 'Administrative Workflow', detail: 'Open the human-review queue and inspect the case timeline.' },
  { id: 'analytics', icon: BarChart3, title: 'Governance Analytics', detail: 'Refresh derived indicators and review items requiring attention.' },
  { id: 'reports', icon: FileDown, title: 'Privacy-safe Report', detail: 'Download a governance-safe CSV from the analytics workspace.' },
]

export default function DemoGuide({ onClose, onNavigate }) {
  const closeRef = useRef(null)
  useEffect(() => {
    const previousFocus = document.activeElement
    closeRef.current?.focus()
    const onKeyDown = (event) => { if (event.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKeyDown)
    return () => {
      window.removeEventListener('keydown', onKeyDown)
      previousFocus?.focus?.()
    }
  }, [onClose])
  return <div className="fixed inset-0 z-[110] flex items-end justify-center bg-black/60 p-0 sm:items-center sm:p-4" role="dialog" aria-modal="true" aria-labelledby="demo-guide-title">
    <section className="flex max-h-[94vh] w-full max-w-2xl flex-col overflow-hidden rounded-t-2xl bg-white shadow-2xl sm:rounded-2xl">
      <header className="flex items-start justify-between gap-4 bg-ink p-5 text-white"><div><p className="text-[9px] font-extrabold uppercase tracking-[.2em] text-lime">Judge-ready walkthrough · navigation only</p><h2 id="demo-guide-title" className="mt-1 font-display text-xl font-extrabold">LANDSTACK Demo Guide</h2><p className="mt-1 text-[10px] leading-relaxed text-white/60">Recommended parcel: RTN-CHI-0013 · Chiplun Demo Village</p></div><button ref={closeRef} onClick={onClose} className="rounded-xl bg-white/10 p-2 hover:bg-white/20" aria-label="Close demo guide"><X size={18} /></button></header>
      <div className="overflow-y-auto p-4 sm:p-5"><p className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-[10px] leading-relaxed text-amber-950">The guide only opens existing views. It never creates, updates, resolves, or deletes workflow records. Fallback workflow records exist only for the current backend session.</p><ol className="mt-4 space-y-2">{steps.map(({ id, icon: Icon, title, detail }, index) => <li key={id} className="flex items-center gap-3 rounded-xl border border-ink/10 p-3"><span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-sand text-xs font-extrabold text-moss">{index + 1}</span><Icon size={17} className="shrink-0 text-moss" /><div className="min-w-0 flex-1"><h3 className="text-xs font-extrabold">{title}</h3><p className="mt-0.5 text-[10px] leading-relaxed text-ink/50">{detail}</p></div><button onClick={() => onNavigate(id)} className="shrink-0 rounded-lg bg-ink px-3 py-2 text-[10px] font-bold text-white">Open</button></li>)}</ol></div>
      <footer className="border-t bg-sand/50 p-4 text-[10px] leading-relaxed text-ink/60">Automated analysis supports prioritization and does not replace official field verification or administrative decision-making.</footer>
    </section>
  </div>
}
