-- LANDSTACK Phase 2: synthetic parcel intelligence schema.
-- No person-identifying ownership data is stored.
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS administrative_boundaries (
    id BIGSERIAL PRIMARY KEY,
    boundary_type TEXT NOT NULL CHECK (boundary_type IN ('village', 'taluka', 'district')),
    name TEXT NOT NULL, code TEXT UNIQUE,
    geometry geometry(MultiPolygon, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS administrative_boundaries_geometry_gix ON administrative_boundaries USING GIST (geometry);

CREATE TABLE IF NOT EXISTS land_parcels (
    id BIGSERIAL PRIMARY KEY,
    parcel_id VARCHAR(32) NOT NULL UNIQUE,
    survey_number VARCHAR(64) NOT NULL,
    village VARCHAR(120) NOT NULL,
    taluka VARCHAR(120) NOT NULL,
    district VARCHAR(120) NOT NULL,
    area_hectares NUMERIC(12, 4) NOT NULL CHECK (area_hectares > 0),
    land_type VARCHAR(80) NOT NULL,
    land_use VARCHAR(80) NOT NULL,
    record_status VARCHAR(80) NOT NULL,
    verification_status VARCHAR(80) NOT NULL,
    risk_status VARCHAR(80) NOT NULL,
    record_reference VARCHAR(64) NOT NULL UNIQUE,
    record_type VARCHAR(120) NOT NULL DEFAULT 'Synthetic Parcel Record',
    source_label VARCHAR(120) NOT NULL DEFAULT 'LANDSTACK Demo Dataset',
    is_synthetic BOOLEAN NOT NULL DEFAULT TRUE CHECK (is_synthetic = TRUE),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    geometry geometry(Polygon, 4326) NOT NULL
);
CREATE INDEX IF NOT EXISTS land_parcels_geometry_gix ON land_parcels USING GIST (geometry);
CREATE INDEX IF NOT EXISTS land_parcels_parcel_id_idx ON land_parcels (parcel_id);
CREATE INDEX IF NOT EXISTS land_parcels_survey_number_idx ON land_parcels (survey_number);
CREATE INDEX IF NOT EXISTS land_parcels_village_idx ON land_parcels (village);
CREATE INDEX IF NOT EXISTS land_parcels_taluka_idx ON land_parcels (taluka);
CREATE INDEX IF NOT EXISTS land_parcels_land_use_idx ON land_parcels (land_use);
CREATE INDEX IF NOT EXISTS land_parcels_verification_status_idx ON land_parcels (verification_status);
CREATE INDEX IF NOT EXISTS land_parcels_risk_status_idx ON land_parcels (risk_status);

CREATE TABLE IF NOT EXISTS parcel_imagery (
    id BIGSERIAL PRIMARY KEY,
    parcel_id VARCHAR(32) NOT NULL REFERENCES land_parcels(parcel_id) ON DELETE CASCADE,
    capture_date DATE NOT NULL,
    image_type VARCHAR(80) NOT NULL,
    image_path TEXT NOT NULL,
    source_label VARCHAR(120) NOT NULL,
    resolution_m NUMERIC(8, 2),
    is_demo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (parcel_id, capture_date)
);
CREATE INDEX IF NOT EXISTS parcel_imagery_parcel_id_idx ON parcel_imagery (parcel_id);

CREATE TABLE IF NOT EXISTS change_analysis (
    id BIGSERIAL PRIMARY KEY,
    parcel_id VARCHAR(32) NOT NULL REFERENCES land_parcels(parcel_id) ON DELETE CASCADE,
    before_image_id BIGINT NOT NULL REFERENCES parcel_imagery(id),
    after_image_id BIGINT NOT NULL REFERENCES parcel_imagery(id),
    analysis_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    changed_area_sqm NUMERIC(14, 2) NOT NULL,
    change_percentage NUMERIC(8, 3) NOT NULL,
    change_strength VARCHAR(32) NOT NULL,
    change_status VARCHAR(80) NOT NULL,
    analysis_method VARCHAR(160) NOT NULL,
    requires_verification BOOLEAN NOT NULL,
    result_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (before_image_id <> after_image_id)
);
CREATE INDEX IF NOT EXISTS change_analysis_parcel_id_idx ON change_analysis (parcel_id);
CREATE INDEX IF NOT EXISTS change_analysis_result_metadata_gin ON change_analysis USING GIN (result_metadata);

CREATE TABLE IF NOT EXISTS parcel_priority_scores (
    id BIGSERIAL PRIMARY KEY,
    parcel_id VARCHAR(32) NOT NULL REFERENCES land_parcels(parcel_id) ON DELETE CASCADE,
    priority_score INTEGER NOT NULL CHECK (priority_score BETWEEN 0 AND 100),
    priority_level VARCHAR(80) NOT NULL,
    requires_field_verification BOOLEAN NOT NULL,
    score_version VARCHAR(32) NOT NULL DEFAULT 'phase4-v1',
    factor_breakdown JSONB NOT NULL,
    recommendation TEXT NOT NULL,
    calculated_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (parcel_id, score_version)
);
CREATE INDEX IF NOT EXISTS parcel_priority_scores_score_idx ON parcel_priority_scores (priority_score DESC);
CREATE INDEX IF NOT EXISTS parcel_priority_scores_level_idx ON parcel_priority_scores (priority_level);

CREATE TABLE IF NOT EXISTS field_inspections (
    id BIGSERIAL PRIMARY KEY,
    inspection_id VARCHAR(40) NOT NULL UNIQUE,
    submission_key VARCHAR(80) NOT NULL UNIQUE,
    parcel_id VARCHAR(32) NOT NULL REFERENCES land_parcels(parcel_id) ON DELETE CASCADE,
    inspection_status VARCHAR(40) NOT NULL CHECK (inspection_status IN ('Not Inspected', 'Inspection Scheduled', 'Inspection In Progress', 'Inspection Completed')),
    inspection_outcome VARCHAR(80) NOT NULL CHECK (inspection_outcome IN ('No Significant Issue Observed', 'Requires Further Review', 'Change Confirmed On Site', 'Unable To Verify')),
    inspection_date TIMESTAMPTZ NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ NOT NULL,
    latitude DOUBLE PRECISION CHECK (latitude BETWEEN -90 AND 90),
    longitude DOUBLE PRECISION CHECK (longitude BETWEEN -180 AND 180),
    gps_accuracy_m DOUBLE PRECISION CHECK (gps_accuracy_m >= 0),
    location_source VARCHAR(40) NOT NULL CHECK (location_source IN ('Browser GPS', 'Manual', 'Unavailable')),
    officer_display_name VARCHAR(100) NOT NULL,
    officer_reference VARCHAR(60) NOT NULL,
    observations TEXT NOT NULL CHECK (char_length(observations) BETWEEN 10 AND 2000),
    recommendation TEXT,
    priority_score_at_inspection INTEGER NOT NULL CHECK (priority_score_at_inspection BETWEEN 0 AND 100),
    priority_level_at_inspection VARCHAR(80) NOT NULL,
    satellite_change_percentage_at_inspection DOUBLE PRECISION,
    requires_follow_up BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (inspection_outcome = 'Unable To Verify' OR (latitude IS NOT NULL AND longitude IS NOT NULL))
);
CREATE INDEX IF NOT EXISTS field_inspections_parcel_idx ON field_inspections (parcel_id);
CREATE INDEX IF NOT EXISTS field_inspections_status_idx ON field_inspections (inspection_status);
CREATE INDEX IF NOT EXISTS field_inspections_outcome_idx ON field_inspections (inspection_outcome);
CREATE INDEX IF NOT EXISTS field_inspections_date_idx ON field_inspections (inspection_date DESC);

CREATE TABLE IF NOT EXISTS inspection_evidence (
    id BIGSERIAL PRIMARY KEY,
    evidence_id VARCHAR(40) NOT NULL UNIQUE,
    inspection_id VARCHAR(40) NOT NULL REFERENCES field_inspections(inspection_id) ON DELETE CASCADE,
    evidence_type VARCHAR(20) NOT NULL DEFAULT 'Photo' CHECK (evidence_type IN ('Photo', 'Document', 'Other')),
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    mime_type VARCHAR(50) NOT NULL CHECK (mime_type IN ('image/jpeg', 'image/png', 'image/webp')),
    file_size_bytes BIGINT NOT NULL CHECK (file_size_bytes BETWEEN 1 AND 5242880),
    caption VARCHAR(500),
    captured_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (inspection_id, evidence_id)
);

CREATE TABLE IF NOT EXISTS citizen_grievances (
    id BIGSERIAL PRIMARY KEY,
    grievance_id VARCHAR(40) NOT NULL UNIQUE,
    submission_key VARCHAR(80) NOT NULL UNIQUE,
    parcel_id VARCHAR(32) NOT NULL REFERENCES land_parcels(parcel_id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL CHECK (category IN ('Land Record Correction Request', 'Boundary / Parcel Concern', 'Suspected Land-Use Change', 'Access / Right-of-Way Concern', 'Public Land Concern', 'Record Information Request', 'Other')),
    custom_category VARCHAR(120),
    description TEXT NOT NULL CHECK (char_length(description) BETWEEN 20 AND 3000),
    status VARCHAR(50) NOT NULL DEFAULT 'Submitted' CHECK (status IN ('Submitted', 'Under Review', 'Field Verification Recommended', 'Resolved', 'Closed', 'More Information Required')),
    priority_reference VARCHAR(40),
    submitted_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    requires_field_verification BOOLEAN NOT NULL DEFAULT FALSE,
    resolution_note TEXT,
    storage_mode VARCHAR(20) NOT NULL CHECK (storage_mode IN ('database', 'fallback')),
    citizen_display_name VARCHAR(100),
    contact_reference VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (category <> 'Other' OR NULLIF(trim(custom_category), '') IS NOT NULL)
);
CREATE INDEX IF NOT EXISTS citizen_grievances_parcel_idx ON citizen_grievances (parcel_id);
CREATE INDEX IF NOT EXISTS citizen_grievances_category_idx ON citizen_grievances (category);
CREATE INDEX IF NOT EXISTS citizen_grievances_status_idx ON citizen_grievances (status);
CREATE INDEX IF NOT EXISTS citizen_grievances_submitted_idx ON citizen_grievances (submitted_at DESC);

CREATE TABLE IF NOT EXISTS grievance_evidence (
    id BIGSERIAL PRIMARY KEY,
    evidence_id VARCHAR(40) NOT NULL UNIQUE,
    grievance_id VARCHAR(40) NOT NULL REFERENCES citizen_grievances(grievance_id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    mime_type VARCHAR(50) NOT NULL CHECK (mime_type IN ('image/jpeg', 'image/png', 'image/webp')),
    file_size_bytes BIGINT NOT NULL CHECK (file_size_bytes BETWEEN 1 AND 5242880),
    caption VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (grievance_id, evidence_id)
);

CREATE TABLE IF NOT EXISTS administrative_cases (
    id BIGSERIAL PRIMARY KEY,
    case_id VARCHAR(40) NOT NULL UNIQUE,
    grievance_id VARCHAR(40) NOT NULL UNIQUE REFERENCES citizen_grievances(grievance_id) ON DELETE RESTRICT,
    parcel_id VARCHAR(32) NOT NULL REFERENCES land_parcels(parcel_id) ON DELETE RESTRICT,
    case_status VARCHAR(50) NOT NULL CHECK (case_status IN ('Open', 'Under Review', 'Field Verification Requested', 'More Information Required', 'Ready for Decision', 'Resolved', 'Closed')),
    review_stage VARCHAR(40) NOT NULL CHECK (review_stage IN ('Intake', 'Initial Review', 'Evidence Review', 'Field Verification', 'Decision Review', 'Finalized')),
    assigned_officer_display VARCHAR(100) NOT NULL,
    assigned_officer_reference VARCHAR(80) NOT NULL,
    opened_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    requires_field_verification BOOLEAN NOT NULL DEFAULT FALSE,
    requires_more_information BOOLEAN NOT NULL DEFAULT FALSE,
    administrative_summary TEXT,
    resolution_type VARCHAR(100),
    resolution_note TEXT,
    latest_priority_score INTEGER NOT NULL CHECK (latest_priority_score BETWEEN 0 AND 100),
    latest_priority_level VARCHAR(40) NOT NULL,
    storage_mode VARCHAR(20) NOT NULL CHECK (storage_mode IN ('database', 'fallback')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS administrative_cases_grievance_idx ON administrative_cases (grievance_id);
CREATE INDEX IF NOT EXISTS administrative_cases_parcel_idx ON administrative_cases (parcel_id);
CREATE INDEX IF NOT EXISTS administrative_cases_status_idx ON administrative_cases (case_status);
CREATE INDEX IF NOT EXISTS administrative_cases_stage_idx ON administrative_cases (review_stage);
CREATE INDEX IF NOT EXISTS administrative_cases_opened_idx ON administrative_cases (opened_at DESC);
CREATE INDEX IF NOT EXISTS administrative_cases_updated_idx ON administrative_cases (updated_at DESC);

CREATE TABLE IF NOT EXISTS administrative_case_events (
    id BIGSERIAL PRIMARY KEY,
    event_id VARCHAR(50) NOT NULL UNIQUE,
    action_key VARCHAR(80) UNIQUE,
    case_id VARCHAR(40) NOT NULL REFERENCES administrative_cases(case_id) ON DELETE CASCADE,
    event_type VARCHAR(60) NOT NULL,
    from_status VARCHAR(50),
    to_status VARCHAR(50),
    from_stage VARCHAR(40),
    to_stage VARCHAR(40),
    note TEXT NOT NULL CHECK (char_length(note) BETWEEN 10 AND 3000),
    actor_display VARCHAR(100) NOT NULL,
    actor_reference VARCHAR(80) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS administrative_case_events_case_idx ON administrative_case_events (case_id, created_at);
