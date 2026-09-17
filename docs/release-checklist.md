# LANDSTACK Release Checklist

Use this checklist before publishing a release. Record only results that were actually verified.

## Automated verification

- [ ] Fresh backend virtual environment created outside the repository
- [ ] Backend dependencies installed from `backend/requirements-dev.txt`
- [ ] Backend application imports and starts
- [ ] Backend test suite passes
- [ ] Fresh frontend install completes with `npm ci`
- [ ] Frontend ESLint passes
- [ ] Frontend production build passes
- [ ] `npm audit` reports no known vulnerabilities

## Safety and data handling

- [ ] Working tree and staged content reviewed
- [ ] Secret scan completed without exposed credentials
- [ ] Privacy scan completed
- [ ] Runtime uploads, generated output, caches, virtual environments, dependencies, and build output are excluded
- [ ] Required synthetic parcel data and demo imagery are included
- [ ] CSV formula-injection protection passes
- [ ] CSV reports contain governance-safe fields only
- [ ] `git diff --cached --check` passes

## Product verification

- [ ] GIS and Parcel Intelligence regression completed
- [ ] Satellite change analysis completed with `RTN-CHI-0013`
- [ ] Inspection priority explanation verified
- [ ] Field-inspection workflow verified
- [ ] Citizen grievance submission and tracking verified
- [ ] Administrative case lifecycle and timeline verified
- [ ] Citizen tracking contains no private administrative notes
- [ ] Governance Analytics refresh and derived totals verified
- [ ] Five CSV report downloads verified
- [ ] Empty, loading, failure, success, and fallback states reviewed
- [ ] Browser console contains no application errors
- [ ] Responsive layouts checked at 375 px, 768 px, and 1440 px
- [ ] Keyboard navigation, labels, visible focus, and reduced-motion behavior checked

## Submission readiness

- [ ] README reviewed
- [ ] Architecture document reviewed
- [ ] Demo script rehearsed
- [ ] Demo recovery guide verified
- [ ] Final screenshots selected intentionally
- [ ] SIH submission checklist reviewed
- [ ] Repository remote and ownership confirmed
- [ ] First local commit reviewed and created
- [ ] GitHub publication completed, or documented as awaiting confirmed remote/authentication
- [ ] SIH submission material checked against the current SIH portal

## Environment limitations to disclose

- [ ] PostgreSQL/PostGIS and database-mode analytics marked **NOT VERIFIED** if not tested
- [ ] Session-scoped fallback persistence disclosed
- [ ] OpenStreetMap internet dependency disclosed
- [ ] Physical-device GPS/camera verification status disclosed
- [ ] Synthetic-data and human-in-the-loop disclaimers remain visible
