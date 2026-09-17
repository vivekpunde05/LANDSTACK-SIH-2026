-- Additive Phase 2 upgrade for a database previously initialized by Phase 1.
-- Existing columns and rows are preserved; deprecated Phase 1 fields are not used by Phase 2.
CREATE EXTENSION IF NOT EXISTS postgis;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='land_parcels' AND column_name='village_name') THEN
        ALTER TABLE land_parcels RENAME COLUMN village_name TO village;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='land_parcels' AND column_name='taluka_name') THEN
        ALTER TABLE land_parcels RENAME COLUMN taluka_name TO taluka;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='land_parcels' AND column_name='district_name') THEN
        ALTER TABLE land_parcels RENAME COLUMN district_name TO district;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='land_parcels' AND column_name='geom') THEN
        ALTER TABLE land_parcels RENAME COLUMN geom TO geometry;
    END IF;
END $$;

ALTER TABLE land_parcels
    ADD COLUMN IF NOT EXISTS parcel_id VARCHAR(32),
    ADD COLUMN IF NOT EXISTS land_type VARCHAR(80) DEFAULT 'Unclassified demo land',
    ADD COLUMN IF NOT EXISTS record_status VARCHAR(80) DEFAULT 'Active',
    ADD COLUMN IF NOT EXISTS risk_status VARCHAR(80) DEFAULT 'Normal',
    ADD COLUMN IF NOT EXISTS record_reference VARCHAR(64),
    ADD COLUMN IF NOT EXISTS record_type VARCHAR(120) DEFAULT 'Synthetic Parcel Record',
    ADD COLUMN IF NOT EXISTS source_label VARCHAR(120) DEFAULT 'LANDSTACK Demo Dataset',
    ADD COLUMN IF NOT EXISTS notes TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS land_parcels_parcel_id_unique_idx ON land_parcels (parcel_id);
CREATE UNIQUE INDEX IF NOT EXISTS land_parcels_record_reference_unique_idx ON land_parcels (record_reference);
CREATE INDEX IF NOT EXISTS land_parcels_geometry_gix ON land_parcels USING GIST (geometry);
CREATE INDEX IF NOT EXISTS land_parcels_parcel_id_idx ON land_parcels (parcel_id);
CREATE INDEX IF NOT EXISTS land_parcels_survey_number_idx ON land_parcels (survey_number);
CREATE INDEX IF NOT EXISTS land_parcels_village_idx ON land_parcels (village);
CREATE INDEX IF NOT EXISTS land_parcels_taluka_idx ON land_parcels (taluka);
CREATE INDEX IF NOT EXISTS land_parcels_land_use_idx ON land_parcels (land_use);
CREATE INDEX IF NOT EXISTS land_parcels_verification_status_idx ON land_parcels (verification_status);
CREATE INDEX IF NOT EXISTS land_parcels_risk_status_idx ON land_parcels (risk_status);
