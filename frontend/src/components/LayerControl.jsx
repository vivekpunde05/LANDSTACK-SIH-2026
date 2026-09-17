import { Layers3, X } from 'lucide-react'

const options = [
  { key: 'parcels', label: 'Land parcels', color: '#d8ff78' },
  { key: 'village', label: 'Village boundary', color: '#f59e0b' },
  { key: 'taluka', label: 'Taluka boundary', color: '#7c3aed' },
]

export default function LayerControl({ layers, setLayers, open, onClose }) {
  return (
    <section className={`${open ? 'flex' : 'hidden'} absolute left-3 top-3 z-20 w-[calc(100%-1.5rem)] max-w-[270px] flex-col overflow-hidden rounded-2xl border border-ink/10 bg-white/95 shadow-panel backdrop-blur md:left-5 md:top-5 md:flex`}>
      <div className="flex items-center justify-between border-b border-ink/10 px-4 py-3">
        <div className="flex items-center gap-2 text-sm font-bold"><Layers3 size={17} /> Map layers</div>
        <button onClick={onClose} className="rounded-lg p-1 text-ink/60 hover:bg-sand md:hidden" aria-label="Close layers"><X size={18} /></button>
      </div>
      <div className="space-y-3 p-4">
        {options.map((option) => (
          <label key={option.key} className="flex cursor-pointer items-center justify-between gap-3 text-sm">
            <span className="flex items-center gap-2.5">
              <span className="h-3 w-3 rounded-sm border border-black/15" style={{ background: option.color }} />
              {option.label}
            </span>
            <input
              type="checkbox"
              checked={layers[option.key]}
              onChange={() => setLayers((current) => ({ ...current, [option.key]: !current[option.key] }))}
              className="h-4 w-4 accent-moss"
            />
          </label>
        ))}
      </div>
      <div className="border-t border-ink/10 bg-sand/70 px-4 py-3 text-[11px] leading-relaxed text-ink/65">
        Boundaries and parcels are fictional demonstration geometry.
      </div>
    </section>
  )
}
