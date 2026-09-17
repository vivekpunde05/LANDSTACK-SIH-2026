-- Phase 3 database-ready imagery history and analysis records.
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
