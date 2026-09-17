# LANDSTACK 5–7 Minute Demonstration

## Before presenting

1. Start FastAPI and the React frontend using the README Quick Start commands.
2. Open `http://127.0.0.1:5173` and confirm the **Local Demo Mode** message is visible when PostGIS is unavailable.
3. Use **Start Demo** to confirm every guide destination opens.
4. For a clean fallback workflow, restart FastAPI immediately before the presentation. This clears session-only inspections, grievances, and cases; it does not alter parcel data or imagery.
5. Keep one genuine JPEG/PNG/WEBP image under 5 MB ready if evidence upload will be shown. Do not use personal material.

Recommended parcel: **RTN-CHI-0013** in Chiplun Demo Village. It has synthetic record metadata, 2023/2026 demo imagery, a meaningful detected change, and an explainable inspection-priority score.

## Presenter flow

### 0:00–0:30 — Problem and product

Open LANDSTACK. Explain that fragmented parcel, imagery, inspection, grievance, and review information makes prioritization difficult. Point out **SIH 2026 Prototype** and **Demo / Synthetic Data**. LANDSTACK is decision support, not a legal-decision system.

### 0:30–1:15 — GIS Explorer

Open **Start Demo → GIS Intelligence**. Show `RTN-CHI-0013`, the parcel highlight, boundaries, search/filter controls, and the Overview/Records tabs. State that the geometry and record are synthetic.

### 1:15–2:00 — Satellite analysis

Reopen **Start Demo → Satellite Analysis**. Compare 2023 and 2026, run change detection, and show the overlay, percentage, approximate area, main region, and explanation. Emphasize that the result indicates visual change only and requires human verification.

### 2:00–2:40 — Inspection priority

Open **Start Demo → Inspection Priority**. Explain the deterministic score factor-by-factor: satellite change, verification status, record status, existing review status, and recency. Open the full Inspection Priority queue and show sorting and filters.

### 2:40–3:30 — Field verification

From the selected parcel or priority queue, choose **Start Inspection**. Show one-time browser location capture, manual-coordinate fallback, required observations, conservative outcomes, follow-up, and protected photo preview. Submit only if you intend to create a session record. Explain that location is captured only on submission and is excluded from governance reports.

### 3:30–4:15 — Citizen grievance

Open **Citizen Grievances**. Search for `RTN-CHI-0013`, submit a concise synthetic concern, optionally attach a safe demo image, and retain the generated `GRV-...` reference. Track it to show the citizen-safe response. No personal contact field is required.

### 4:15–5:15 — Administrative review

In the Grievance Queue, choose **Open Case**, then **View Case**. Show the linked parcel, grievance, satellite, priority, inspection/evidence context, administrative review, and timeline. Follow only the actions returned by the backend:

1. Start Review with a clear synthetic note.
2. If a completed inspection exists, optionally request field verification, return to inspection, then resume review.
3. Mark Ready for Decision.
4. Resolve with a controlled resolution type and note.
5. Close the case.

Track the grievance again. Confirm it shows only public status, stage, date, and permitted resolution type—never internal notes or event history.

### 5:15–6:00 — Governance analytics and reports

Open **Governance Analytics**, select **Refresh Analytics**, and relate the updated counts to the records just created. Show distributions, taluka activity, and Requires Attention. Download a CSV report and explain the privacy allowlist and formula-injection protection.

### 6:00–6:30 — Architecture, privacy, and cost

Summarize the path: GIS → change detection → priority → human field verification → grievance/case review → descriptive analytics. State that no Aadhaar, demographic scoring, legal conclusion, paid API, paid cloud, or credit card is required.

## Reliable fallback sequence

Fallback workflow data is process-local. If the backend restarts mid-demo, existing grievance, inspection, and case references disappear. Start again at the relevant form, generate a new reference, and continue; never claim that fallback records are durable.
