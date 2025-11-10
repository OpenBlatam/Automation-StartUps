-- Schema para versionado de descripciones de puesto

CREATE TABLE IF NOT EXISTS job_description_versions (
    version_id SERIAL PRIMARY KEY,
    job_description_id INTEGER REFERENCES job_descriptions(job_description_id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    role VARCHAR(255),
    level VARCHAR(50),
    department VARCHAR(255),
    required_skills JSONB,
    preferred_skills JSONB,
    location VARCHAR(255),
    version_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(job_description_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_versions_job_desc ON job_description_versions(job_description_id);
CREATE INDEX IF NOT EXISTS idx_versions_number ON job_description_versions(version_number);
CREATE INDEX IF NOT EXISTS idx_versions_created ON job_description_versions(created_at);

-- Vista de versiones recientes
CREATE OR REPLACE VIEW recent_versions AS
SELECT 
    v.version_id,
    v.job_description_id,
    jd.role,
    v.version_number,
    v.version_notes,
    v.created_at
FROM job_description_versions v
JOIN job_descriptions jd ON v.job_description_id = jd.job_description_id
ORDER BY v.created_at DESC
LIMIT 100;






