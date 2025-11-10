-- =============================================================
-- BloodConnect — PostGIS-enabled schema (fixed)
-- Ensures PostGIS functions exist and uses proper casts/indexes.
-- Adds a generated geography column for fast radius queries.
-- =============================================================

-- 1) Enable PostGIS in THIS database
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- 2) Core tables
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  phone TEXT UNIQUE,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'PATIENT',
  referal_code TEXT UNIQUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS donors (
  user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  full_name TEXT NOT NULL,
  blood_group TEXT NOT NULL,
  city TEXT, state TEXT, pincode TEXT,
  latitude NUMERIC(9,6),                 -- store as numeric to keep input flexible
  longitude NUMERIC(9,6),
  -- Generated geography point for PostGIS queries (null-safe if lat/lon null)
  geom geography(Point,4326) GENERATED ALWAYS AS (
    CASE
      WHEN latitude IS NULL OR longitude IS NULL
      THEN NULL
      ELSE ST_SetSRID(ST_MakePoint(longitude::double precision, latitude::double precision), 4326)::geography
    END
  ) STORED,
  available BOOLEAN DEFAULT TRUE,
  last_donation_date DATE,
  donations_count INT DEFAULT 0,
  medical_flags JSONB DEFAULT '{}'::jsonb,
  fcm_token TEXT
);

-- Spatial index on generated geography column
CREATE INDEX IF NOT EXISTS donors_geom_gist ON donors USING GIST (geom);

CREATE TABLE IF NOT EXISTS patient_requests (
  id TEXT PRIMARY KEY,
  requester_user_id TEXT REFERENCES users(id),
  patient_name TEXT NOT NULL,
  required_blood_group TEXT NOT NULL,
  units INT NOT NULL DEFAULT 1,
  hospital_name TEXT NOT NULL,
  city TEXT,
  latitude NUMERIC(9,6),
  longitude NUMERIC(9,6),
  -- Optional generated geography for requests too
  geom geography(Point,4326) GENERATED ALWAYS AS (
    CASE
      WHEN latitude IS NULL OR longitude IS NULL
      THEN NULL
      ELSE ST_SetSRID(ST_MakePoint(longitude::double precision, latitude::double precision), 4326)::geography
    END
  ) STORED,
  needed_by DATE,
  notes TEXT,
  status TEXT DEFAULT 'OPEN',
  phone TEXT,
  registerd_user BOOLEAN DEFAULT TRUE
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS requests_geom_gist ON patient_requests USING GIST (geom);

CREATE TABLE IF NOT EXISTS matches (
  id TEXT PRIMARY KEY,
  request_id TEXT REFERENCES patient_requests(id) ON DELETE CASCADE,
  donor_user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
  match_score NUMERIC(5,2),
  status TEXT DEFAULT 'SENT',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  responded_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
  token TEXT PRIMARY KEY,
  user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
  expires_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS batches (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  city TEXT,
  scheduled_on DATE,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS batch_donors (
  batch_id TEXT REFERENCES batches(id) ON DELETE CASCADE,
  donor_user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
  PRIMARY KEY (batch_id, donor_user_id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  method TEXT,
  path TEXT,
  status_code INT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================
-- 3) Helpful checks (optional)
-- Run these manually in psql/pgAdmin:
-- SELECT postgis_full_version();
-- SELECT ST_AsText(ST_MakePoint(85.8245::double precision, 20.2685::double precision));
-- SELECT COUNT(*) FROM donors;
-- =============================================================
