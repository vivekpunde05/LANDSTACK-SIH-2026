-- Safe additive Phase 6 citizen grievance and evidence storage.
CREATE TABLE IF NOT EXISTS citizen_grievances (
    id BIGSERIAL PRIMARY KEY,
    grievance_id VARCHAR(40) NOT NULL UNIQUE,
    submission_key VARCHAR(80) NOT NULL UNIQUE,
    parcel_id VARCHAR(32) NOT NULL REFERENCES land_parcels(parcel_id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL CHECK (category IN (
        'Land Record Correction Request', 'Boundary / Parcel Concern',
        'Suspected Land-Use Change', 'Access / Right-of-Way Concern',
        'Public Land Concern', 'Record Information Request', 'Other'
    )),
    custom_category VARCHAR(120),
    description TEXT NOT NULL CHECK (char_length(description) BETWEEN 20 AND 3000),
    status VARCHAR(50) NOT NULL DEFAULT 'Submitted' CHECK (status IN (
        'Submitted', 'Under Review', 'Field Verification Recommended',
        'Resolved', 'Closed', 'More Information Required'
    )),
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
