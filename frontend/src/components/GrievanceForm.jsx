import { useEffect, useRef, useState } from 'react'
import { AlertCircle, Camera, Check, Clipboard, LoaderCircle, MessageSquareWarning, Trash2, X } from 'lucide-react'
import { grievanceCategories } from '../data/grievanceOptions'

const allowedTypes = new Set(['image/jpeg', 'image/png', 'image/webp'])
const allowedExtensions = new Set(['jpg', 'jpeg', 'png', 'webp'])
const MAX_BYTES = 5 * 1024 * 1024

const responseError = async (response) => {
  try { return (await response.json()).detail?.message || 'Grievance could not be submitted.' }
  catch { return 'Grievance could not be submitted.' }
}

export default function GrievanceForm({ parcel, onClose, onCompleted, completionLabel = 'Close' }) {
  const [category, setCategory] = useState('')
  const [customCategory, setCustomCategory] = useState('')
  const [description, setDescription] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [photos, setPhotos] = useState([])
  const [photoError, setPhotoError] = useState('')
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [success, setSuccess] = useState(null)
  const [copyState, setCopyState] = useState('')
  const submissionKey = useRef(globalThis.crypto?.randomUUID?.().replaceAll('-', '') || `grievance${Date.now()}`)
  const photosRef = useRef([])
  photosRef.current = photos
  useEffect(() => () => photosRef.current.forEach((photo) => URL.revokeObjectURL(photo.preview)), [])

  const addPhotos = (event) => {
    const incoming = [...event.target.files]
    event.target.value = ''
    setPhotoError('')
    if (photos.length + incoming.length > 3) { setPhotoError('A maximum of 3 images is allowed.'); return }
    for (const file of incoming) {
      const extension = file.name.split('.').pop()?.toLowerCase()
      if (!allowedTypes.has(file.type) || !allowedExtensions.has(extension)) { setPhotoError('Only JPEG, PNG, and WEBP images are allowed.'); return }
      if (file.size > MAX_BYTES) { setPhotoError('Each image must be 5 MB or smaller.'); return }
    }
    setPhotos((current) => [...current, ...incoming.map((file) => ({ file, preview: URL.createObjectURL(file) }))])
  }
  const removePhoto = (index) => setPhotos((current) => current.filter((photo, itemIndex) => {
    if (itemIndex === index) URL.revokeObjectURL(photo.preview)
    return itemIndex !== index
  }))
  const validate = () => {
    if (!category) return 'Choose a grievance category.'
    if (category === 'Other' && !customCategory.trim()) return 'Enter a short custom category note.'
    if (description.trim().length < 20 || description.trim().length > 3000) return 'Description must contain 20–3000 characters.'
    return ''
  }
  const submit = async (event) => {
    event.preventDefault()
    if (submitting || success) return
    const error = validate()
    if (error) { setFormError(error); return }
    setFormError(''); setSubmitting(true)
    const form = new FormData()
    form.append('payload', JSON.stringify({
      category, custom_category: category === 'Other' ? customCategory.trim() : null,
      description: description.trim(), citizen_display_name: displayName.trim() || null,
      contact_reference: null,
    }))
    photos.forEach(({ file }) => form.append('photos', file))
    try {
      const response = await fetch(`/api/parcels/${encodeURIComponent(parcel.parcel_id)}/grievances`, { method: 'POST', headers: { 'X-Idempotency-Key': submissionKey.current }, body: form })
      if (!response.ok) throw new Error(await responseError(response))
      const result = await response.json()
      setSuccess(result); onCompleted?.(result)
    } catch (error) {
      setFormError(error.message || 'Submission failed. Check the backend and try again.'); setSubmitting(false)
    }
  }
  const copyReference = async () => {
    try {
      if (!navigator.clipboard) throw new Error()
      await navigator.clipboard.writeText(success.grievance_id)
      setCopyState('Reference copied.')
    } catch { setCopyState('Clipboard unavailable — select and copy the reference manually.') }
  }

  return <div className="fixed inset-0 z-[70] overflow-y-auto bg-ink/70 p-2 backdrop-blur-sm sm:p-5" role="dialog" aria-modal="true" aria-label="Citizen grievance form">
    <div className="mx-auto min-h-full max-w-2xl rounded-2xl bg-white shadow-2xl sm:min-h-0">
      <header className="sticky top-0 z-10 flex items-start justify-between rounded-t-2xl bg-ink px-4 py-4 text-white sm:px-6"><div><p className="text-[9px] font-extrabold uppercase tracking-[.18em] text-lime">Citizen Grievance · Demo</p><h2 className="mt-1 font-display text-xl font-extrabold">Report a Parcel Concern</h2><p className="text-[10px] text-white/55">{parcel.parcel_id} · Survey {parcel.survey_number}</p></div><button type="button" onClick={onClose} className="rounded-xl bg-white/10 p-2" aria-label="Close grievance form"><X size={19} /></button></header>
      {success ? <div className="grid min-h-[520px] place-items-center p-6 text-center"><div className="max-w-md"><Check className="mx-auto text-emerald-600" size={50} /><h3 className="mt-4 font-display text-xl font-extrabold">Grievance submitted successfully</h3><p className="mt-4 text-[10px] font-bold uppercase tracking-wider text-ink/45">Reference</p><p className="mt-1 select-all font-display text-2xl font-extrabold">{success.grievance_id}</p><p className="mt-1 text-xs font-bold">Status: {success.status}</p><p className="mt-3 text-xs text-ink/55">Keep this grievance reference for tracking.</p><button onClick={copyReference} className="mt-4 inline-flex items-center gap-2 rounded-xl border border-ink/15 px-4 py-2.5 text-xs font-bold"><Clipboard size={15} /> Copy Reference</button>{copyState && <p role="status" className="mt-2 text-[10px] text-moss">{copyState}</p>}<p className="mt-4 rounded-xl bg-amber-50 p-3 text-[10px] text-amber-900">{success.storage_notice}</p><button onClick={onClose} className="mt-4 rounded-xl bg-ink px-5 py-3 text-xs font-bold text-white">{completionLabel}</button></div></div> : <form onSubmit={submit} className="space-y-5 p-4 sm:p-6">
        <section className="rounded-2xl bg-sand/65 p-4"><h3 className="text-[10px] font-extrabold uppercase tracking-widest text-moss">Parcel context</h3><div className="mt-3 grid grid-cols-2 gap-3 text-xs sm:grid-cols-4"><div><span className="text-ink/45">Parcel ID</span><p className="font-bold">{parcel.parcel_id}</p></div><div><span className="text-ink/45">Survey</span><p className="font-bold">{parcel.survey_number}</p></div><div><span className="text-ink/45">Village</span><p className="font-bold">{parcel.village}</p></div><div><span className="text-ink/45">Taluka</span><p className="font-bold">{parcel.taluka}</p></div></div></section>
        <div className="rounded-xl border border-blue-200 bg-blue-50 p-3 text-[10px] leading-relaxed text-blue-900"><strong>Important:</strong> Citizen-submitted information requires official verification and does not constitute a legal determination.</div>
        <section><label className="text-xs font-extrabold">Category <span className="text-rose-600">*</span><select aria-label="Grievance category" value={category} onChange={(event) => setCategory(event.target.value)} className="mt-2 h-11 w-full rounded-xl border border-ink/15 px-3 text-sm font-normal"><option value="">Choose category…</option>{grievanceCategories.map((value) => <option key={value}>{value}</option>)}</select></label>{category === 'Other' && <label className="mt-3 block text-xs font-extrabold">Custom category note <span className="text-rose-600">*</span><input aria-label="Custom grievance category" value={customCategory} onChange={(event) => setCustomCategory(event.target.value)} maxLength={120} className="mt-2 h-11 w-full rounded-xl border border-ink/15 px-3 text-sm font-normal" /></label>}</section>
        <section><label className="text-xs font-extrabold">Description <span className="text-rose-600">*</span><textarea aria-label="Grievance description" value={description} onChange={(event) => setDescription(event.target.value)} maxLength={3000} rows={6} placeholder="Describe the concern and what information should be reviewed…" className="mt-2 w-full resize-y rounded-xl border border-ink/15 p-3 text-sm font-normal" /></label><p className="text-right text-[9px] text-ink/40">{description.length} / 3000</p></section>
        <section><label className="text-xs font-extrabold">Demo citizen display name <span className="font-normal text-ink/45">(optional)</span><input aria-label="Citizen display name" value={displayName} onChange={(event) => setDisplayName(event.target.value)} maxLength={100} placeholder="Optional demo name" className="mt-2 h-11 w-full rounded-xl border border-ink/15 px-3 text-sm font-normal" /></label><p className="mt-1 text-[9px] text-ink/45">Do not enter Aadhaar, phone numbers, a full address, or government identification.</p></section>
        <section><div className="flex items-center justify-between gap-3"><div><h3 className="text-xs font-extrabold">Supporting images</h3><p className="text-[10px] text-ink/50">JPEG, PNG, or WEBP · 5 MB each · maximum 3</p></div><label className="flex shrink-0 cursor-pointer items-center gap-2 rounded-xl bg-sand px-3 py-2 text-xs font-bold"><Camera size={15} /> Add Images<input type="file" accept="image/jpeg,image/png,image/webp" multiple onChange={addPhotos} className="sr-only" /></label></div>{photoError && <p role="alert" className="mt-2 text-[10px] font-bold text-rose-700">{photoError}</p>}<div className="mt-3 grid grid-cols-3 gap-2">{photos.map((photo, index) => <div key={photo.preview} className="relative overflow-hidden rounded-xl border border-ink/10"><img src={photo.preview} alt={`Grievance evidence preview ${index + 1}`} className="aspect-square w-full object-cover" /><button type="button" onClick={() => removePhoto(index)} className="absolute right-1 top-1 rounded-lg bg-ink/85 p-1.5 text-white" aria-label={`Remove grievance image ${index + 1}`}><Trash2 size={13} /></button></div>)}</div></section>
        {formError && <div role="alert" className="flex gap-2 rounded-xl bg-rose-50 p-3 text-xs font-semibold text-rose-800"><AlertCircle size={16} className="shrink-0" />{formError}</div>}
        <div className="sticky bottom-0 -mx-4 flex gap-3 border-t border-ink/10 bg-white/95 p-4 backdrop-blur sm:-mx-6 sm:px-6"><button type="button" onClick={onClose} className="h-12 flex-1 rounded-xl border border-ink/15 text-xs font-bold">Cancel</button><button type="submit" disabled={submitting} className="flex h-12 flex-[2] items-center justify-center gap-2 rounded-xl bg-ink text-xs font-bold text-white disabled:opacity-60">{submitting ? <><LoaderCircle size={16} className="animate-spin" /> Submitting…</> : <><MessageSquareWarning size={16} /> Submit Grievance</>}</button></div>
      </form>}
    </div>
  </div>
}
