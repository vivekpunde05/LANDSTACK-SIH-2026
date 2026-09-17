# LANDSTACK Prototype Architecture

## Integrated governance workflow

```text
Synthetic parcel + imagery data
              |
              v
        GIS Intelligence <----------------------+
              |                                 |
              v                                 |
      Explainable Change Detection              |
              |                                 |
              v                                 |
       Inspection Priority ----------------> Priority Queue
              |                                 |
              v                                 |
       Field Verification <----------+          |
              |                      |          |
              v                      |          |
       Inspection History            |          |
                                     |          |
Citizen Grievance --> Tracking --> Administrative Case Review
                                     |          |
                                     +----------+
                                     |
                                     v
                         Governance Analytics + Reports
```

The arrows describe information flow, not automatic legal decisions. A grievance can inform administrative review; a case can request field verification; inspection evidence returns to the case; and all existing operational state contributes to descriptive analytics. The backend remains authoritative for validation and status transitions.

The React shell keeps GIS Explorer immediately available and lazy-loads non-critical queue, analytics, case-detail, inspection-form, and parcel-tab modules. Every lazy boundary has a visible loading state. The Demo Guide invokes existing navigation callbacks only and never mutates workflow state.

## Primary data path

```text
Browser
  React dashboard
  OpenLayers map
       |
       | GET /api/parcels + query filters
       | GET /api/parcels/{parcel_id}
       v
FastAPI
  parcel router
  parcel query service
       |
       | parameterized SQL via SQLAlchemy
       v
PostgreSQL + PostGIS
  land_parcels
  Polygon geometry, SRID 4326
  GIST spatial index + attribute indexes
```

## Fallback path

```text
API or database unavailable
       |
       v
Visible warning in React
       |
       v
Local deterministic synthetic GeoJSON
       |
       v
Client-side search/filter + OpenLayers
```

The fallback never presents itself as a live database connection. Both paths contain only synthetic, non-personal records with no legal validity.

## Phase 3 imagery path

```text
Parcel Intelligence / Satellite History
       |
       | select 2023 and 2026 demo captures
       v
FastAPI imagery router
       |
       v
Local synthetic PNG pair
       |
       v
OpenCV LAB difference -> threshold -> morphology -> connected regions
       |
       +--> changed percentage + approximate area + conservative status
       +--> generated mask and visual overlay (ignored by Git)
```

The local manifest keeps the demo operational when PostGIS is unavailable. The schema remains ready to persist imagery metadata and analysis results once a database runtime is available. Future adapters may source public Sentinel-2 or Landsat imagery without changing the UI or analysis contract.

## Phase 4 inspection-priority path

```text
GIS / synthetic parcel data
       |
       +--> Phase 3 satellite change analysis
       |
       v
Current parcel record, verification, and review state
       |
       v
Deterministic Inspection Priority Engine (phase4-v1)
       |
       +--> five scored factors + plain-language reasons
       +--> 0–100 workflow score + non-legal priority level
       |
       v
Inspection Priority Queue
       |
       v
Human field verification workflow (Phase 5)
```

Weights and thresholds are centralized in `backend/app/services/priority_engine.py`. A missing satellite analysis contributes zero change and recency points. It is not treated as adverse evidence. If PostGIS is connected, the score is upserted into `parcel_priority_scores`; otherwise the API returns the same calculated result with an explicit persistence warning.

Only synthetic operational attributes influence the score. Personal, ownership, political, income, and demographic attributes are neither stored nor scored. The engine ranks workflow attention and cannot establish a legal condition.

## Phase 5 human verification path

```text
Inspection Priority Queue
       |
       v
Parcel selection and read-only intelligence context
       |
       v
Responsive field inspection form
       |
       +--> one-time browser GPS OR validated manual coordinates
       +--> required observations and conservative outcome
       +--> zero to three locally previewed photos
       |
       v
Atomic validated multipart submission + idempotency key
       |
       +--> PostgreSQL metadata mirror when available
       +--> locked current-session fallback when unavailable
       +--> safe generated evidence filenames in ignored local storage
       |
       v
Inspection history and evidence viewer
       |
       v
Citizen grievance and administrative review
```

The browser makes no background location requests and stores nothing before submission. FastAPI validates the entire inspection and all photos before assigning an inspection ID. Database failure is never hidden: the record is returned with `storage_mode: fallback` and a restart-loss notice. The Phase 4 score formula remains unchanged; inspection context is captured as a historical snapshot only.

## Phase 6 citizen grievance path

```text
Citizen
   |
   v
Synthetic parcel search or map selection
   |
   v
Validated grievance + optional image evidence
   |
   +--> server-generated grievance reference
   +--> idempotent duplicate protection
   +--> explicit PostgreSQL or current-session fallback mode
   |
   v
Reference-based citizen tracking + parcel grievance history
   |
   v
Newest-first Grievance Queue
   |
   v
Administrative Review (Phase 7)
   |
   v
Possible explicit inspection or controlled resolution (never automatic)
```

Phase 6 reuses the Phase 5 image validator and safe file-storage pattern. FastAPI validates the category, Other-category note, 20–3000 character description, count, size, extension, MIME type, and file signature before creating a record. Runtime files receive random server names and can only be fetched through a grievance/evidence association. The public response excludes the contact reference.

Fallback creation, tracking, history, and queue reads are protected by one process lock. An idempotency key maps uncertain retries to the original grievance. The fallback is intentionally session-scoped, reports database unavailability, and makes no durable-storage claim. A database connection mirrors the same metadata into the additive Phase 6 tables.

Citizen submissions always begin as `Submitted`. Phase 7 may synchronize public grievance status through controlled case actions, but it does not alter the Phase 4 priority formula or create field inspections automatically. All reports require official verification and cannot establish legality, wrongdoing, ownership, or enforcement action.

## Phase 7 administrative review path

```text
Grievance Queue
       |
       | idempotent Open Case
       v
Administrative Case / Intake
       |
       v
Initial Review
       |
       +--> request field verification --> existing Phase 5 inspection form
       |                                      |
       |                                      v
       |                                Evidence Review
       |
       +--> request more information -------> Evidence Review
       |
       +--> review satellite, priority, inspections, and evidence
       |
       v
Ready for Decision
       |
       v
Controlled Resolution --> Closed
       |
       +--> append-only internal event timeline
       +--> citizen-safe grievance status and resolution type
```

FastAPI owns the lifecycle rules and returns `allowed_actions` with the case detail. React does not infer a second transition table; it renders only the supplied actions and disables them while a request is running. Required notes, controlled resolution types, completed-inspection checks, and idempotency keys are validated again on the server.

One grievance can open at most one case. Current case state is stored in `administrative_cases`; immutable workflow events are stored separately in `administrative_case_events`. A lock protects the equivalent current-session fallback store, and each successful case mutation attempts an additive database mirror without hiding connection failure.

Citizen tracking calls the grievance service, which attaches a deliberately narrow case summary: case reference, public status, review stage, last update, and a controlled resolution type only after resolution. It omits administrative notes and summaries, event history, officer reference, and linked evidence details.

The demonstration actor is synthetic (`DEMO-ADMIN-01`), and authentication or role-based authorization is intentionally deferred. Administrative output is workflow decision support and cannot determine ownership, legality, wrongdoing, or enforcement.

## Phase 8 descriptive analytics path

```text
Synthetic GIS parcel records
       + Phase 3 actual demo analyses
       + Phase 4 calculated priorities
       + Phase 5 current inspections
       + Phase 6 current grievances
       + Phase 7 current administrative cases
                         |
                         v
             Read-only analytics snapshot
                         |
          +--------------+---------------+
          |              |               |
       Summary     Distributions     Geography
          |              |               |
          +--------------+---------------+
                         |
                 Attention Queue
                         |
                         v
             Governance Analytics UI
                         |
                         v
       Privacy-whitelisted UTF-8 CSV reports
```

The backend takes one clean snapshot per analytics request from existing application services. No parallel demo dataset, aggregate table, predictive model, or scheduled polling is introduced. Summary, distribution, geography, and attention endpoints are intentionally separate so the user controls refresh timing and each response stays explainable.

All distributions include their controlled labels even when counts are zero. Percentage functions explicitly handle an empty denominator. Resolution rate is `null` when there are no cases, and average satellite change is `null` when there are no actual analyses. The frontend renders both as `N/A`, never as a fabricated 0% result.

Reports use fixed field allowlists. Grievance exports omit citizen identity/contact fields; inspection exports omit coordinates and observations; case exports omit administrative notes, summaries, and actor references. Evidence names, storage paths, and internal filesystem details are excluded everywhere. Spreadsheet formula prefixes are neutralized before standard-library CSV serialization.

No Phase 8 migration exists or is required. In the current environment, parcel analytics are derived from the synthetic application dataset and workflow analytics from the same locked process-local fallback stores used by Phases 5–7. The dashboard explicitly labels this current-session scope. A future database-backed reader can replace the snapshot adapter without changing metric definitions or report contracts.

Phase 8 is descriptive and operational. It does not forecast grievances, predict wrongdoing, create a new risk score, or produce official government statistics.

## Query safety

- All user-provided search/filter values are bound parameters.
- Filter column names are selected from a fixed application list.
- No ownership, demographic, or personally identifying fields exist in the data or scoring model.
- The seed is idempotent on `parcel_id`.
- GeoJSON output is produced from PostGIS with `ST_AsGeoJSON`.
- Change outputs are decision-support indicators and never legal determinations.
- Inspection outcomes represent field observations only and never establish legality.
- Evidence access requires both the inspection ID and an associated server-generated evidence ID.
- Raw upload names are never used as filesystem paths.
- Grievance categories and statuses are controlled enums; citizen-created records always start as `Submitted`.
- Grievance tracking responses omit contact references and expose no sensitive identity fields.
- Grievance evidence uses the shared file-signature validator and requires both associated server IDs.
- Case actions are selected from a controlled enum and rejected unless valid for the current server-side status.
- Administrative event notes are internal and are not included in citizen grievance tracking responses.
- One case per grievance plus per-action idempotency prevents duplicate cases and duplicate timeline events.
- Analytics and reports use fixed aggregate definitions and privacy-safe column allowlists.
- Empty denominators return zero distribution percentages or `N/A` rates, never NaN or Infinity.
- CSV cells with formula prefixes are neutralized before download.
