# LANDSTACK Demo Recovery Guide

Use these steps during preparation or a live SIH demonstration. They do not delete source data, alter Git, or require paid services.

## Backend is not running

```bash
cd /path/to/LANDSTACK-SIH-2026/backend
.venv/bin/python -m uvicorn app.main:app --reload
```

If the relocated `.venv` launchers fail, recreate the ignored environment using the README Quick Start instructions. Do not patch or commit `.venv` binaries.

## Frontend is not running

```bash
cd /path/to/LANDSTACK-SIH-2026/frontend
npm run dev
```

Open `http://127.0.0.1:5173`.

## Port 8000 or 5173 is occupied

Prefer stopping only the old LANDSTACK development process. If that is not possible, run FastAPI on another local port and explicitly point Vite to it:

```bash
cd backend
.venv/bin/python -m uvicorn app.main:app --port 8003

cd ../frontend
VITE_BACKEND_TARGET=http://127.0.0.1:8003 npm run dev -- --port 5176
```

Then open `http://127.0.0.1:5176`.

## Local Demo Mode banner appears

This is expected when PostgreSQL/PostGIS is unavailable. Parcel data, local imagery, change detection, priority calculation, and session-only workflows remain available. Do not claim database persistence is active.

## Map tiles do not load

OpenStreetMap background tiles require internet. Synthetic parcel polygons and boundaries are vector data bundled with the app and should remain visible over the plain map background. Continue using parcel search, selection, intelligence tabs, and workflows. Do not switch to a paid basemap.

## Workflow session was reset

FastAPI restart clears fallback inspection, grievance, and case metadata. Resubmit a synthetic grievance or inspection and use the newly generated reference. Parcel data, imagery, and priority calculations are unaffected.

For a deliberate clean demo session, restart only FastAPI before the presentation. Runtime uploads/generated outputs are ignored by Git; do not delete them during a live recovery.

## CSV download does not appear

1. Confirm FastAPI is running and Governance Analytics loads.
2. Select **Refresh Analytics**.
3. Retry **Download CSV** and check the browser downloads control.
4. If blocked, allow downloads for the local `127.0.0.1` page.

Do not copy private data into a replacement spreadsheet. The backend report is the privacy-safe source.

## GPS permission is denied or unavailable

Do not repeatedly request permission. Enter valid latitude/longitude manually, or choose **Unable To Verify** when location cannot be established. LANDSTACK does not continuously track location and stores it only when the inspection is submitted.

## Uploaded image is rejected

Use a genuine JPEG, PNG, or WEBP image no larger than 5 MB. Renaming another format is insufficient because the backend validates extension, MIME type, and file signature. A maximum of three images is allowed.

## Change analysis fails

Use one of the four imagery-enabled parcels: `RTN-RAT-0001`, `RTN-RAT-0002`, `RTN-CHI-0013`, or `RTN-SAN-0019`. Confirm the backend can write to ignored `backend/generated/`, then retry with Before 2023 and After 2026.

## Final pre-demo check

```bash
cd /path/to/LANDSTACK-SIH-2026/backend
.venv/bin/python -m pytest -q

cd ../frontend
npm run lint
npm run build
npm audit
```
