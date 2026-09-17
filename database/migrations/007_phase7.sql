-- Safe additive Phase 7 administrative case and immutable event history.
CREATE TABLE IF NOT EXISTS administrative_cases (
    id BIGSERIAL PRIMARY KEY,
    case_id VARCHAR(40) NOT NULL UNIQUE,
    grievance_id VARCHAR(40) NOT NULL UNIQUE REFERENCES citizen_grievances(grievance_id) ON DELETE RESTRICT,
    parcel_id VARCHAR(32) NOT NULL REFERENCES land_parcels(parcel_id) ON DELETE RESTRICT,
    case_status VARCHAR(50) NOT NULL CHECK (case_status IN (
        'Open', 'Under Review', 'Field Verification Requested',
        'More Information Required', 'Ready for Decision', 'Resolved', 'Closed'
    )),
    review_stage VARCHAR(40) NOT NULL CHECK (review_stage IN (
        'Intake', 'Initial Review', 'Evidence Review', 'Field Verification',
        'Decision Review', 'Finalized'
    )),
    assigned_officer_display VARCHAR(100) NOT NULL,
    assigned_officer_reference VARCHAR(80) NOT NULL,
    opened_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    requires_field_verification BOOLEAN NOT NULL DEFAULT FALSE,
    requires_more_information BOOLEAN NOT NULL DEFAULT FALSE,
    administrative_summary TEXT,
    resolution_type VARCHAR(100) CHECK (resolution_type IS NULL OR resolution_type IN (
        'No Further Action Required', 'Record Review Recommended',
        'Field Verification Completed', 'Additional Documentation Required',
        'Referred for Further Administrative Review', 'Information Updated in Case Record',
        'Unable to Conclude from Available Evidence'
    )),
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
