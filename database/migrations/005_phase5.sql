-- Safe additive Phase 5 field-inspection and evidence storage.
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
