# LANDSTACK

**Integrated GIS Digital Public Infrastructure for Land Governance**

[![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-Fast%20Build%20Tool-646CFF?logo=vite&logoColor=white)](https://vite.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-UI%20Styling-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![OpenLayers](https://img.shields.io/badge/OpenLayers-GIS%20Mapping-1F6B75?logo=openlayers&logoColor=white)](https://openlayers.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![PostGIS](https://img.shields.io/badge/PostGIS-3.4-4A90E2?logo=postgresql&logoColor=white)](https://postgis.net/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![NumPy](https://img.shields.io/badge/NumPy-Scientific%20Computing-013243?logo=numpy&logoColor=white)](https://numpy.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerization-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
Smart India Hackathon 2026 · Problem statement **SIH26014**

LANDSTACK is a free/open-source SIH prototype that connects parcel intelligence, visual change analysis, explainable inspection priority, field verification, citizen grievances, administrative review, and governance analytics in one GIS workspace. It remains demonstrable in an explicit local fallback mode when PostgreSQL/PostGIS is unavailable.

![LANDSTACK GIS Explorer](docs/screenshots/01-gis-explorer.png)

*The GIS Explorer presents synthetic Ratnagiri-area parcels, fictional administrative boundaries, layer controls, and OpenStreetMap context.*

> **Synthetic dataset disclaimer:** LANDSTACK currently uses synthetic demonstration parcel data. It does not represent official cadastral, ownership, or legal land records. No real person, ownership detail, Aadhaar number, phone number, or personal address is stored.

## Project overview

The project demonstrates a transparent GIS workflow in which a web interface requests filtered GeoJSON from an API backed by spatially indexed PostGIS records. It uses only local, free, and open-source components and requires no paid API or credit card.

**Workflow:** Parcel Intelligence → Satellite Change Analysis → Inspection Priority → Field Verification → Citizen Grievance → Administrative Review → Governance Analytics

## Key capabilities

- GIS parcel search, filtering, boundaries, selection, and structured records
- Explainable before/after change detection using local synthetic imagery
- Deterministic inspection-priority scoring and field-verification workflow
- Citizen grievance submission, safe tracking, and administrative review
- Derived governance analytics and privacy-safe CSV reports
- Explicit local demo mode when PostgreSQL/PostGIS is unavailable

Use **Start Demo** in the application sidebar for a navigation-only walkthrough. The recommended judge-demo parcel is `RTN-CHI-0013`, which has parcel metadata, imagery, a meaningful change result, and an explainable priority score. The guide never creates or mutates workflow records.

## Prototype showcase

### GIS Explorer & Parcel Intelligence

| GIS workspace | Selected parcel intelligence |
| --- | --- |
| ![LANDSTACK GIS Explorer with synthetic parcels](docs/screenshots/01-gis-explorer.png) | ![LANDSTACK Parcel Intelligence for RTN-CHI-0013](docs/screenshots/02-parcel-intelligence.png) |

Search and filters update the live parcel layer, while selecting a parcel opens its structured, non-personal land record context.

### Satellite Change Intelligence

![LANDSTACK synthetic imagery change analysis](docs/screenshots/03-satellite-change.png)

LANDSTACK compares **synthetic demonstration imagery** and highlights potential visual change for human verification. The result is indicative decision-support—not cadastral evidence or a legal determination.

### Explainable Inspection Priority

![LANDSTACK explainable inspection priority](docs/screenshots/04-priority-explanation.png)

The deterministic priority score shows every contributing workflow factor and its points; it does not score ownership, illegality, or personal characteristics.

### Field & Citizen Workflows

| Field inspection | Citizen grievance receipt |
| --- | --- |
| ![LANDSTACK completed demo field inspection](docs/screenshots/05-field-inspection.png) | ![LANDSTACK synthetic citizen grievance receipt](docs/screenshots/06-citizen-grievance.png) |

Responsive forms support human field observations and privacy-conscious citizen reporting, with explicit current-session fallback behavior.

### Administrative Review

![LANDSTACK completed administrative case](docs/screenshots/07-administrative-review.png)

The case workspace links grievance, parcel, satellite, priority, inspection, evidence, review, and event context through backend-validated transitions.

### Governance Analytics

![LANDSTACK governance analytics dashboard](docs/screenshots/08-governance-analytics.png)

All dashboard values are derived from the current synthetic parcel and workflow records; no predictive or fabricated statistics are used.

## Demo

A short LANDSTACK prototype walkthrough will be added here.

## Phase status

### Phase 1 — Completed

- Responsive React dashboard and OpenLayers map
- 24 synthetic parcel polygons and synthetic boundaries
- Pan, zoom, hover, click, legend, and layer toggles
- FastAPI foundation and offline fallback

### Phase 2 — Completed

- PostgreSQL/PostGIS schema with spatial and attribute indexes
- Idempotent 24-parcel seed process
- PostGIS-backed GeoJSON, detail, search, and filter API
- Database-aware health response
- Parcel Intelligence panel with functional Overview and Records tabs
- Search selection with map focus, four filter categories, result counts, and clear filters
- Explicit loading, empty, unavailable, and fallback states

### Phase 3 — Completed

- Functional Satellite History tab for four synthetic demo parcels
- Deterministic 2023/2026 before-and-after imagery pairs
- Explainable OpenCV/NumPy change-detection pipeline
- Side-by-side comparison, change overlay, and binary mask views
- Approximate changed area and percentage based on parcel area
- Conservative `No significant change detected`, `Potential change`, and `Requires verification` results
- Human-readable changed-region explanation and field-verification recommendation
- Database-ready `parcel_imagery` and `change_analysis` tables

### Phase 4 — Completed

- Deterministic, rule-based Inspection Priority Score from 0–100
- Central scoring weights, versioned as `phase4-v1`
- Complete factor-by-factor explanations and workflow recommendations
- Ranked Inspection Priority Queue with level, taluka, verification, and minimum-score filters
- Functional Priority tab inside Parcel Intelligence
- Database-ready score persistence with safe calculation-only operation when PostGIS is unavailable
- No personal, demographic, ownership, or legally determinative inputs

### Phase 5 — Completed

- Responsive browser-based field inspection form from Parcel Intelligence and the Priority Queue
- One-time browser GPS capture with manual-coordinate fallback
- Strict coordinate, observation, outcome, and follow-up validation
- Preview/remove workflow for up to three JPEG, PNG, or WEBP photos
- Server-side file signature, MIME, extension, 5 MB, traversal, and filename protections
- Idempotency-key protection against accidental duplicate submissions
- Inspection history, latest status, evidence thumbnails, and simple evidence viewer
- Additive PostGIS-ready inspection/evidence schema and explicit current-session fallback mode

### Phase 6 — Completed

- Citizen-facing parcel search and validated grievance submission
- Controlled grievance categories, server-generated references, and `Submitted` initial status
- Optional preview/remove workflow for up to three protected JPEG, PNG, or WEBP evidence images
- Citizen receipt, copy-reference control, and reference-based status tracking
- Functional Grievances tab with parcel history and restricted evidence viewing
- Newest-first officer Grievance Queue with status, category, and taluka filters
- Idempotency-key duplicate protection and explicit current-session fallback mode
- Additive PostGIS-ready grievance and grievance-evidence schema

### Phase 7 — Completed

- Administrative Review dashboard with derived case counts and queue filters
- One idempotently opened administrative case per grievance
- Case Detail views for grievance, satellite, priority, inspections, evidence, review, and timeline context
- Backend-authoritative, validated lifecycle actions with required administrative notes
- Append-only case event timeline and traceable `phase7-v1` workflow
- Synchronized citizen-safe grievance status and public case summary
- Explicit current-session fallback operation when PostgreSQL/PostGIS is unavailable
- Additive PostGIS-ready administrative case and immutable event schema

### Phase 8 — Completed

- Derived Governance Analytics summary, distributions, geographic activity, and attention queue
- Accessible dependency-free CSS bar charts with labels, counts, percentages, and empty states
- Explicit metric definitions, refresh timestamp, and fallback-mode disclosure
- Satellite overview averaging only parcels with actual analyses
- Five governance-safe UTF-8 CSV reports with formula-injection protection
- Aggregate/private-data boundaries for grievances, inspections, and administrative cases
- Descriptive operational analytics only—no prediction, new score, or fabricated trend

### Phase 9 — Completed

- Functional navigation labels with no dead placeholder destinations
- Global SIH prototype and synthetic-data identity
- Navigation-only judge Demo Guide centered on `RTN-CHI-0013`
- Consistent local-demo, human-in-the-loop, loading, and empty-state language
- Keyboard focus visibility, reduced-motion handling, and offline-safe system fonts
- Safe view-level code splitting for non-critical dashboards and workflow panels
- Reproducible clean-environment instructions, presenter script, and recovery guide

### Phase 10 — Completed

- Clean backend and frontend dependency-install verification
- Final security, privacy, legal-language, repository, and CSV audits
- Full automated and browser regression gates
- Release, SIH submission, screenshot, demonstration, and recovery checklists
- First-commit and GitHub publication safety gates

Authentication, scheduling, notifications, enforcement, and predictive analytics remain intentionally excluded.

## Quick start — local demo mode

Docker is optional for the working synthetic demonstration. From a fresh clone:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

In a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

Open <http://127.0.0.1:5173>. The app clearly reports **Local Demo Mode** when PostgreSQL/PostGIS is unavailable. Parcel, imagery, priority, and current-session workflow demonstrations remain usable; OpenStreetMap background tiles require internet access.

## Architecture

```text
React + Tailwind + OpenLayers
             |
             v
          FastAPI
             |
             +--> Satellite change analysis
             |              |
             |              v
             +--> Inspection Priority Engine --> Priority Queue
             |                                  |
             |                                  v
             +------------------------> Field Inspection
                                                |
                                                v
                                GPS + observations + evidence
             |
             +--> Citizen Grievance --> Reference + tracking
                                      |
                                      v
                                Grievance Queue
                                      |
                                      v
                         Administrative Case Review
                                      |
                       +--------------+--------------+
                       |                             |
                 Event Timeline            Citizen-safe Status
                                      |
                                      v
                    Governance Analytics + CSV Reports
             |
             v
   PostgreSQL + PostGIS (when available)

Local synthetic GeoJSON
             |
             v
     Fallback only when API/PostGIS is unavailable
```

See `docs/architecture.md` for the request and fallback flow.

## Technology stack

| Layer | Free/open-source technology |
|---|---|
| UI | React, Vite, Tailwind CSS, Lucide React |
| GIS | OpenLayers, GeoJSON, OpenStreetMap development tiles |
| API | FastAPI, Uvicorn |
| Data access | SQLAlchemy, GeoAlchemy2, psycopg 3 |
| Spatial database | PostgreSQL 16, PostGIS 3.4 |
| Local orchestration | Docker Compose |

## Project structure

```text
landstack/
├── frontend/src/
│   ├── components/       # Map, workflows, analytics, and Demo Guide
│   └── data/             # Synthetic boundaries and fallback parcels
├── backend/app/
│   ├── models/           # Parcel and Phase 3–7 workflow models
│   ├── routers/          # Parcel, workflow, analytics, and report endpoints
│   ├── schemas/          # Structured API schemas
│   └── services/         # Existing data sources and derived analytics
├── backend/tests/
├── database/
│   ├── schema.sql
│   ├── migrations/       # Additive Phase 2–7 upgrades
│   └── seed_parcels.py   # Idempotent parcel + imagery metadata seed
├── datasets/satellite/   # Small synthetic demo imagery pairs
├── scripts/generate_demo_imagery.py
├── docs/
│   ├── architecture.md
│   ├── demo-script.md
│   ├── demo-recovery.md
│   ├── release-checklist.md
│   ├── sih-submission-checklist.md
│   └── screenshot-plan.md
├── docker-compose.yml
├── .env.example
└── README.md
```

## Environment configuration

Copy the example and choose a local-only password:

```bash
cp .env.example .env
```

Set `POSTGRES_PASSWORD` and use the same password in `DATABASE_URL`. The `.env` file is ignored by Git. Never commit real credentials.

## PostgreSQL/PostGIS and Docker setup

Install Docker Desktop or another Docker Compose-compatible, free/local runtime, then:

```bash
docker compose --env-file .env up -d db
docker compose ps
```

On first creation, the container applies `database/schema.sql`, enables PostGIS, and creates the indexed tables.

For an existing Phase 1 database, apply the additive Phase 2 upgrade before seeding:

```bash
docker compose exec -T db psql -U landstack -d landstack < database/migrations/002_phase2.sql
docker compose exec -T db psql -U landstack -d landstack < database/migrations/003_phase3.sql
docker compose exec -T db psql -U landstack -d landstack < database/migrations/004_phase4.sql
docker compose exec -T db psql -U landstack -d landstack < database/migrations/005_phase5.sql
docker compose exec -T db psql -U landstack -d landstack < database/migrations/006_phase6.sql
docker compose exec -T db psql -U landstack -d landstack < database/migrations/007_phase7.sql
```

Check PostGIS directly:

```bash
docker compose exec db psql -U landstack -d landstack -c "SELECT PostGIS_Version();"
```

## Database seeding

Create a clean backend environment and export the database URL from your private `.env`:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
export DATABASE_URL='postgresql+psycopg://landstack:YOUR_LOCAL_PASSWORD@localhost:5432/landstack'
cd ..
python database/seed_parcels.py
```

The seed uses conflict-safe upserts, so rerunning it updates the same 24 parcels and eight imagery metadata rows rather than duplicating them.

Verify the data:

```bash
docker compose exec db psql -U landstack -d landstack -c \
  "SELECT COUNT(*), COUNT(DISTINCT parcel_id), BOOL_AND(ST_IsValid(geometry)) FROM land_parcels;"
```

Expected result: `24 | 24 | t`.

## Backend setup

```bash
cd backend
source .venv/bin/activate
export DATABASE_URL='postgresql+psycopg://landstack:YOUR_LOCAL_PASSWORD@localhost:5432/landstack'
python -m uvicorn app.main:app --reload
```

`requirements-dev.txt` includes `requirements.txt`, so it installs both runtime and test dependencies. Virtual environments may contain absolute launcher paths; after moving a checkout, recreate `.venv` instead of patching its binaries. The virtual environment is ignored by Git.

## Frontend setup

```bash
cd frontend
npm ci
npm run dev
```

Open <http://127.0.0.1:5173>. Vite proxies `/api` to FastAPI at port 8000.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Application, database, and PostGIS health |
| GET | `/api/parcels` | GeoJSON FeatureCollection |
| GET | `/api/parcels/{parcel_id}` | Structured Parcel Intelligence detail |
| GET | `/api/parcels/{parcel_id}/imagery` | Available synthetic imagery history |
| POST | `/api/parcels/{parcel_id}/change-analysis` | Run deterministic before/after analysis |
| GET | `/api/parcels/{parcel_id}/priority` | Explainable parcel Inspection Priority Score |
| GET | `/api/priorities` | Ranked priority queue with optional filters |
| POST | `/api/parcels/{parcel_id}/inspections` | Create one validated multipart inspection |
| GET | `/api/parcels/{parcel_id}/inspections` | Current parcel inspection history |
| GET | `/api/inspections/{inspection_id}` | Inspection detail |
| POST | `/api/parcels/{parcel_id}/grievances` | Create one validated multipart grievance |
| GET | `/api/parcels/{parcel_id}/grievances` | Parcel grievance history |
| GET | `/api/grievances/{grievance_id}` | Privacy-safe grievance tracking/detail |
| GET | `/api/grievances` | Newest-first grievance queue with optional filters |
| GET | `/api/grievances/{grievance_id}/evidence/{evidence_id}` | Restricted grievance evidence |
| POST | `/api/grievances/{grievance_id}/case` | Open or return the grievance's administrative case |
| GET | `/api/cases` | Administrative queue with optional filters |
| GET | `/api/cases/{case_id}` | Consolidated case detail and allowed actions |
| GET | `/api/cases/{case_id}/events` | Ordered append-only case event timeline |
| POST | `/api/cases/{case_id}/actions` | Apply one backend-validated lifecycle action |
| POST | `/api/cases/{case_id}/notes` | Append an administrative review note |
| GET | `/api/analytics/summary` | Current derived governance metrics |
| GET | `/api/analytics/distributions` | Priority, verification, workflow, and satellite distributions |
| GET | `/api/analytics/geography` | Taluka and village activity aggregation |
| GET | `/api/analytics/attention` | Existing high-priority and unresolved workflow items |
| GET | `/api/reports/parcels.csv` | Governance-safe parcel CSV |
| GET | `/api/reports/priorities.csv` | Inspection Priority CSV |
| GET | `/api/reports/grievances.csv` | Privacy-limited grievance CSV |
| GET | `/api/reports/inspections.csv` | Privacy-limited inspection CSV |
| GET | `/api/reports/cases.csv` | Privacy-limited administrative case CSV |
| GET | `/docs` | Interactive OpenAPI documentation |

Search and filter examples:

```text
/api/parcels?search=SYN-10
/api/parcels?taluka=Chiplun
/api/parcels?land_use=Agricultural
/api/parcels?verification_status=Pending%20Verification
/api/parcels?risk_status=Flagged%20for%20Review
/api/parcels?taluka=Ratnagiri&land_use=Orchard
/api/priorities?level=High%20Priority%20Review
/api/priorities?min_score=50&taluka=Chiplun
/api/priorities?verification_status=Pending%20Verification&limit=10
/api/grievances?status=Submitted
/api/grievances?category=Boundary%20%2F%20Parcel%20Concern&taluka=Ratnagiri
/api/grievances?parcel_id=RTN-RAT-0001&limit=10
/api/cases?status=Under%20Review&taluka=Ratnagiri
/api/cases?stage=Decision%20Review&priority_level=High%20Priority%20Review
```

Search is partial and case-insensitive across parcel ID, survey number, and village. Attribute filters are case-insensitive exact matches.

Run a demo change analysis:

```bash
curl -X POST http://127.0.0.1:8000/api/parcels/RTN-RAT-0002/change-analysis \
  -H 'Content-Type: application/json' \
  -d '{"before_date":"2023-01-01","after_date":"2026-01-01"}'
```

## Satellite History and change detection

Four parcels include small, deterministic, synthetic aerial-style image pairs:

| Parcel | Demo scenario | Expected result class |
|---|---|---|
| `RTN-RAT-0001` | Stable imagery | No significant change detected |
| `RTN-RAT-0002` | Small visual structure appears | Potential change |
| `RTN-CHI-0013` | Moderate ground-cover difference | Requires verification |
| `RTN-SAN-0019` | Vegetation/ground-cover difference | Requires verification |

These assets can be regenerated locally with:

```bash
cd backend
.venv/bin/python ../scripts/generate_demo_imagery.py
```

The classical computer-vision pipeline:

1. Reads and size-aligns the selected images.
2. Converts both images to the LAB color space.
3. Calculates absolute per-pixel visual differences.
4. Applies Gaussian denoising and a fixed demo threshold.
5. Uses morphological opening/closing to remove isolated noise.
6. Finds meaningful connected regions and their primary map quadrant.
7. Converts changed-pixel percentage into an approximate area using the synthetic parcel area.
8. Writes a mask and red-tinted overlay without modifying either source image.

Classical CV was chosen because it is lightweight, deterministic, offline, inspectable, and easy to explain during judging. The thresholds—below 1.5%, 1.5–8%, and above 8%—are prototype heuristics, not scientific confidence scores or government standards. No fabricated AI confidence is returned.

> **Demo imagery disclaimer:** all included imagery is procedurally generated for the prototype workflow. It is not official satellite imagery, cadastral evidence, or proof of a legal condition.

Human review remains mandatory. LANDSTACK may indicate land-cover or visual-feature differences; it cannot establish ownership, legality, encroachment, criminal conduct, or a required government action.

## Inspection Priority Engine

Phase 4 answers a narrow workflow question: which synthetic parcels should officers review first? It is deterministic and rule-based—not machine learned—and every point is accompanied by a plain-language reason.

| Factor | Maximum points |
|---|---:|
| Satellite change signal | 40 |
| Verification status | 20 |
| Record status | 15 |
| Existing review status | 15 |
| Analysis recency | 10 |

Satellite change contributes 0 points without analysis, 0 below 1.5%, 10 from 1.5–4%, 20 from 4–8%, 30 from 8–15%, and 40 above 15%. Lack of imagery is never treated as suspicious. Current synthetic statuses provide the remaining factors, and a recent meaningful 2026 demo analysis contributes 10 recency points (a recent stable analysis contributes 3).

| Total score | Workflow level |
|---|---|
| 0–24 | Routine |
| 25–49 | Review Recommended |
| 50–74 | High Priority Review |
| 75–100 | Urgent Review |

Priority thresholds are prototype heuristics designed for workflow demonstration and are not government or legal standards. The Priority tab exposes all five factor scores, reasons, calculation time, and score version. The queue sorts highest first and its values are derived at runtime rather than hardcoded.

When PostGIS is connected, the latest `phase4-v1` score is upserted into `parcel_priority_scores`. When the database is unavailable, FastAPI explicitly reports that persistence is inactive and still calculates the same result from the local synthetic parcel state and real Phase 3 demo analysis.

No caste, religion, gender, income, owner name, Aadhaar, phone number, political data, demographic characteristic, or other personal information is collected or used. The score prioritizes human review only; it never determines legality, ownership, wrongdoing, or enforcement.

## Field inspection workflow

An officer can start a demo inspection from the Priority Queue or the functional Inspections tab. The form keeps parcel, Phase 4 priority, verification, and Phase 3 change context read-only; only field observations and inspection evidence are submitted.

Location uses a single `navigator.geolocation.getCurrentPosition` request with high accuracy, a 10-second timeout, and a 60-second cached-position allowance. LANDSTACK does not continuously track or submit coordinates before the officer completes the form. Permission denial, timeout, unavailable position, and unsupported browsers produce a visible message and allow manual latitude/longitude entry. Valid coordinates are required except for the `Unable To Verify` outcome.

Supported outcomes are deliberately conservative:

- No Significant Issue Observed
- Requires Further Review
- Change Confirmed On Site
- Unable To Verify

“Change Confirmed On Site” describes a visual or physical observation only. No outcome is a legal determination.

Photo evidence is limited to three files, 5 MB each, in JPEG, PNG, or WEBP format. Both the browser and server validate limits. The server checks extension, declared MIME type, and image signature; removes path components from display names; writes unpredictable server-generated filenames under `backend/uploads/inspections/`; never executes uploads; and exposes only evidence IDs associated with a known inspection. Runtime uploads are ignored by Git.

Every submission includes an idempotency key. The UI disables submission while a request is active, and the backend returns the original inspection if the same key is retried. This prevents double-click and uncertain-network retries from creating duplicate records.

With a connected database, inspection metadata is mirrored to `field_inspections` and `inspection_evidence`. Without PostGIS, records remain in a locked process-local store and uploaded files remain in the ignored upload directory. The UI displays: “Demo inspection stored in local fallback mode — database unavailable.” Current-session inspection metadata disappears when the backend restarts; this limitation is intentionally explicit.

## Citizen grievance workflow

Citizens can search the 24 synthetic parcels, review a parcel’s non-personal context, and submit a demonstration grievance without providing sensitive identity data. Categories are controlled:

- Land Record Correction Request
- Boundary / Parcel Concern
- Suspected Land-Use Change
- Access / Right-of-Way Concern
- Public Land Concern
- Record Information Request
- Other (requires a short custom category)

Every new grievance starts as `Submitted`. Phase 7 can synchronize it to `Under Review`, `Field Verification Recommended`, `More Information Required`, `Resolved`, or `Closed` through the controlled administrative case lifecycle. A citizen report remains an allegation or review request—not a validated fact or legal determination.

The description is required and limited to 20–3000 characters. A display name is optional; Aadhaar, PAN, phone number, full address, government ID, caste, religion, and political information are neither required nor modeled. Responses used for tracking do not expose the optional contact reference.

Evidence uses the proven Phase 5 validator: at most three genuine JPEG, PNG, or WEBP images of 5 MB each. The browser previews files, while FastAPI validates extension, MIME type, and image signature before writing anything. Server-generated filenames, containment checks, associated evidence IDs, and ignored upload directories prevent raw filenames or arbitrary paths from being served.

The server creates references such as `GRV-2026-0001`. An idempotency key makes a repeated submission return the original record rather than creating another. The receipt can copy the reference when the browser clipboard is available; otherwise it leaves the visible reference available for manual copy. Tracking returns only parcel, category, status, dates, and other non-sensitive workflow data.

When PostgreSQL is available, metadata is mirrored to `citizen_grievances` and `grievance_evidence`. Without PostGIS, the locked in-memory store supports creation, tracking, parcel history, queue filters, and evidence during the current backend session. The UI explicitly states: “Demo grievance stored in local fallback mode — database unavailable.” Metadata disappears after restart; runtime image files are not treated as durable records and are excluded from Git.

Citizen-submitted information requires official verification and does not constitute a legal determination. Phase 7 does not change the Phase 4 priority formula and never creates an inspection automatically; an officer must explicitly start the existing Phase 5 form when field verification is requested.

## Administrative case review

Phase 7 converts a submitted grievance into at most one administrative case. Opening the same grievance again or retrying with the same idempotency key returns the existing case rather than creating a duplicate. The dashboard shows workflow-derived counts and a newest-updated-first queue filterable by status, review stage, taluka, and Inspection Priority level.

Case Detail consolidates the linked grievance, safe satellite result, explainable priority, field inspections, associated evidence, administrative controls, and event timeline. The API supplies `allowed_actions`, so the interface displays only actions currently valid for that case while the backend remains authoritative.

The deterministic lifecycle is:

```text
Open / Intake
  -> Under Review / Initial Review
  -> Field Verification Requested OR More Information Required OR Ready for Decision
  -> Under Review / Evidence Review (after requested work or information)
  -> Ready for Decision / Decision Review
  -> Resolved / Finalized
  -> Closed / Finalized
```

Every action requires a 10–3000 character administrative note. Resolving also requires a controlled, non-legal resolution type. Field-verification cases cannot enter decision review until a completed inspection exists. Invalid transitions are rejected by FastAPI, action buttons are disabled while requests run, and idempotency keys prevent duplicate events.

Administrative events are append-only and ordered by creation time. They record the action, prior and resulting status/stage, note, demonstration actor, and timestamp. Citizen tracking receives only case reference, public status, review stage, updated time, and—after resolution—the controlled resolution type. Administrative notes, internal summaries, event history, actor reference, and evidence detail are never exposed through citizen tracking.

With PostgreSQL available, `administrative_cases` and `administrative_case_events` mirror current state and history. When it is unavailable, the locked process-local store keeps the complete demo workflow operational and returns an explicit fallback notice. Fallback cases and events disappear when the backend restarts. Docker/PostGIS persistence has not been verified on the current machine.

This is a human-in-the-loop demonstration. Administrative review organizes evidence and workflow; it does not establish ownership, wrongdoing, legality, or an enforcement outcome.

## Governance analytics and reports

Phase 8 takes one read-only snapshot from the same services used by Phases 1–7: synthetic parcels, actual Phase 3 analyses, Phase 4 priority results, and current inspection, grievance, and administrative-case stores. It does not maintain a separate analytics dataset, store aggregate tables, alter the priority formula, or fabricate historical trends.

Metric definitions are fixed and tested:

| Metric | Definition |
|---|---|
| Total Parcels | Number of parcels currently represented in analytics |
| Review-Recommended Parcels | Priority level is anything other than `Routine` |
| Satellite Analyses | Parcels with an actual available Phase 3 analysis |
| Completed Inspections | Inspection status equals `Inspection Completed` |
| Open Grievances | Status is neither `Resolved` nor `Closed` |
| Active Administrative Cases | Status is neither `Resolved` nor `Closed` |
| Resolved/Closed Cases | Case status is `Resolved` or `Closed` |
| Resolution Rate | Resolved/closed cases divided by all cases; `N/A` when no cases exist |

Distributions preserve the existing controlled priority, verification, grievance, case, inspection, and satellite labels. Percentages are `count / distribution total × 100`; empty distributions return zero-valued rows rather than NaN or Infinity. Average satellite change includes analyzed parcels only—missing imagery is never converted to a false 0% measurement.

Activity by Taluka and Village counts only records linked to parcels in that geography. Taluka rows are sorted by recorded workflow activity, then parcel count. The attention list reuses High/Urgent Phase 4 priorities and unresolved Phase 6–7 statuses; it is not a new score or predictive model.

Five reports are available as UTF-8 CSV: Parcel Summary, Inspection Priority, Grievance Summary, Inspection Summary, and Administrative Case Summary. Column allowlists exclude citizen names/contact references, GPS coordinates, evidence filenames and paths, administrative actor references, internal notes, and filesystem details. Text beginning with spreadsheet formula prefixes (`=`, `+`, `-`, or `@`, including after leading whitespace) is prefixed with an apostrophe to prevent CSV formula injection.

No Phase 8 database migration is required. When PostgreSQL/PostGIS is unavailable, analytics read the same current-session fallback stores and visibly say that the results reflect local demo-session data. Workflow metrics therefore reset with the backend process. The dashboard is descriptive and operational only; it contains no prediction, legal conclusion, or official government statistic.

> **Analytics disclaimer:** LANDSTACK analytics currently use synthetic demonstration parcel data and local prototype workflow records. They do not represent official government statistics.

## Screens and flows

The primary screen remains the GIS Explorer and Parcel Intelligence map. Parcel Intelligence has six functional tabs—Overview, Records, Satellite History, Priority, Inspections, and Grievances—and shows a linked administrative case indicator. Functional sidebar destinations cover GIS Explorer, Inspection Priority, Citizen Grievances, Administrative Review, and Governance Analytics. Case Detail uses a responsive tab strip for its eight context areas. The Demo Guide opens these existing views without mutating records. See the [demo script](docs/demo-script.md), [recovery guide](docs/demo-recovery.md), [release checklist](docs/release-checklist.md), [SIH submission checklist](docs/sih-submission-checklist.md), and [screenshot plan](docs/screenshot-plan.md).

## Tests

```bash
cd backend
.venv/bin/python -m pytest -q

cd ../frontend
npm run lint
npm run build
npm audit --omit=dev
```

Final release verification on 16 September 2026:

| Gate | Result |
|---|---|
| Fresh backend environment from `requirements-dev.txt` | Passed |
| Backend tests | 77 passed |
| Fresh frontend `npm ci` | Passed with an isolated local npm cache |
| ESLint | Passed |
| Production build | Passed; initial application chunk 523.69 kB (157.02 kB gzip) |
| Dependency audit | 0 vulnerabilities |
| Clean fallback browser rehearsal | Passed |
| Responsive checks | 375 px, 768 px, and 1440 px passed without page-level overflow |
| CSV privacy checks | Five reports passed |

The non-failing Vite warning for the OpenLayers/core application chunk remains documented; no risky release-time optimization was introduced merely to suppress it.

## Troubleshooting

- **`docker: command not found`:** install Docker Desktop or a compatible free local container runtime.
- **Compose requests `POSTGRES_PASSWORD`:** create `.env` from `.env.example` and set a local password.
- **Health says `database: unavailable`:** confirm the container is healthy, `DATABASE_URL` matches `.env`, and the seed completed.
- **Frontend says fallback active:** the UI is intentionally using the local synthetic dataset because the API/PostGIS path is unavailable.
- **Moved virtual environment commands fail:** delete and recreate only your local ignored `backend/.venv` using the Quick Start commands. Do not patch or commit environment binaries.
- **Map appears without basemap detail:** internet access is required for OpenStreetMap development tiles; parcel geometry still works locally.
- **Imagery tab is empty:** only four explicitly listed synthetic parcels have demo imagery in Phase 3.
- **Analysis output cannot be written:** ensure `backend/generated/` is writable. The directory is intentionally ignored by Git.
- **Priority says `not persisted`:** this is the expected transparent calculation-only mode when PostGIS is unavailable; start the database and apply migration `004_phase4.sql` to enable persistence.
- **Inspection history is empty after restart:** current-session fallback metadata is intentionally non-persistent. Configure PostGIS and apply `005_phase5.sql` for durable metadata.
- **GPS fails or is denied:** enter coordinates manually, or choose `Unable To Verify` when a valid location cannot be obtained.
- **A photo is rejected:** use a genuine JPEG, PNG, or WEBP file no larger than 5 MB; renaming another file type is not sufficient.
- **Grievance history is empty after restart:** current-session fallback metadata is intentionally non-persistent. Configure PostGIS and apply `006_phase6.sql` for durable metadata.
- **Tracking cannot find a reference:** confirm the reference is exact and that the fallback backend has not restarted since submission.
- **Administrative queue is empty:** create a grievance in Citizen Grievances, then select **Open Case**. Fallback cases disappear after a backend restart.
- **An administrative action is unavailable:** the backend returns actions valid for the current status. Complete the required earlier stage; field-verification cases also require a completed inspection before decision review.
- **Case persistence says fallback:** this is expected without PostgreSQL/PostGIS. Apply `007_phase7.sql` only after migrations 002–006 when a database runtime is available.
- **Analytics show zero grievances, inspections, or cases:** these workflow records are session-scoped in fallback mode and reset when the backend restarts.
- **Resolution rate is N/A:** no administrative cases currently exist, so a percentage would be misleading.
- **A CSV download fails:** confirm FastAPI is running at the Vite proxy target and retry from Governance Analytics.
- **Database was previously created:** schema initialization scripts run only on a new Docker volume. Apply `database/schema.sql` manually or recreate only the project database volume if its data is disposable.

## Limitations and future scope

Future work may add official cadastral validation, free public Sentinel/Landsat ingestion, authentication and role-based authorization, government SSO, durable PostGIS deployment, mobile/PWA field tooling, notifications, and scalable geospatial infrastructure. These are future possibilities, not implemented features. The current fallback workflow is session-scoped, Docker/PostGIS has not been verified on this machine, and public OpenStreetMap development tiles are not an offline or production basemap service.

## Data, cost, and license

The included geometry, metadata, and before/after imagery are synthetic demonstration assets; they are not Sentinel, Landsat, official cadastral, ownership, or legal evidence. Public OpenStreetMap tiles are appropriate only for light development use; production use must follow the tile usage policy or use a self-hosted open stack. Source code is released under the MIT License. LANDSTACK uses only free/open-source/local/browser-native resources in the implemented prototype and requires no payment or credit card.
#

## 👥Team Members

| Name | LinkedIn |
|---|---|
| Aryan Mhatre | [LinkedIn](https://www.linkedin.com/in/aryan-mhatre) |
| Jayveer Talekar | [LinkedIn](https://www.linkedin.com/in/jayveer-talekar) |
| Pragati Sahani | [LinkedIn](https://www.linkedin.com/in/pragati-sahani) |
| Akshata Kamble | [LinkedIn](https://www.linkedin.com/in/akshata-kamble) |
| Afrin Shaikh | [LinkedIn](https://www.linkedin.com/in/afrin-shaikh) |
