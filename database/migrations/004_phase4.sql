-- Safe additive Phase 4 inspection-priority storage.
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
