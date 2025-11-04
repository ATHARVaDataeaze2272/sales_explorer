-- ============================================
-- PostgreSQL Vector Extension Setup
-- ============================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- Table 1: Client Embeddings
-- Stores 3 types of embeddings per client
-- ============================================
CREATE TABLE IF NOT EXISTS client_embeddings (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL,
    document_id INTEGER,
    
    -- Three embedding types (384 dimensions each)
    job_title_embedding vector(384),
    business_area_embedding vector(384),
    activity_embedding vector(384),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key to client_upload_profiles
    CONSTRAINT fk_client_profile 
        FOREIGN KEY (profile_id) 
        REFERENCES client_upload_profiles(id) 
        ON DELETE CASCADE,
    
    -- Ensure one set of embeddings per profile
    CONSTRAINT unique_client_profile UNIQUE (profile_id)
);

-- Indexes for fast vector similarity search (HNSW algorithm)
CREATE INDEX IF NOT EXISTS idx_client_job_title_embedding 
    ON client_embeddings 
    USING hnsw (job_title_embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_client_business_area_embedding 
    ON client_embeddings 
    USING hnsw (business_area_embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_client_activity_embedding 
    ON client_embeddings 
    USING hnsw (activity_embedding vector_cosine_ops);

-- Regular indexes
CREATE INDEX IF NOT EXISTS idx_client_embeddings_profile_id 
    ON client_embeddings(profile_id);

-- ============================================
-- Table 2: Prospect Embeddings
-- Stores 3 types of embeddings per prospect
-- ============================================
CREATE TABLE IF NOT EXISTS prospect_embeddings (
    id SERIAL PRIMARY KEY,
    prospect_id INTEGER NOT NULL,
    document_id INTEGER,
    
    -- Three embedding types (384 dimensions each)
    job_title_embedding vector(384),
    business_area_embedding vector(384),
    expertise_embedding vector(384),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key to prospects
    CONSTRAINT fk_prospect 
        FOREIGN KEY (prospect_id) 
        REFERENCES prospects(id) 
        ON DELETE CASCADE,
    
    -- Ensure one set of embeddings per prospect
    CONSTRAINT unique_prospect UNIQUE (prospect_id)
);

-- Indexes for fast vector similarity search
CREATE INDEX IF NOT EXISTS idx_prospect_job_title_embedding 
    ON prospect_embeddings 
    USING hnsw (job_title_embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_prospect_business_area_embedding 
    ON prospect_embeddings 
    USING hnsw (business_area_embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_prospect_expertise_embedding 
    ON prospect_embeddings 
    USING hnsw (expertise_embedding vector_cosine_ops);

-- Regular indexes
CREATE INDEX IF NOT EXISTS idx_prospect_embeddings_prospect_id 
    ON prospect_embeddings(prospect_id);

-- ============================================
-- Table 3: Client-Prospect Matches
-- Stores matching results
-- ============================================
CREATE TABLE IF NOT EXISTS client_prospect_matches (
    id SERIAL PRIMARY KEY,
    client_profile_id INTEGER NOT NULL,
    prospect_id INTEGER NOT NULL,
    
    -- Similarity scores
    job_title_score DECIMAL(5,4),
    business_area_score DECIMAL(5,4),
    activity_score DECIMAL(5,4),
    overall_score DECIMAL(5,4) NOT NULL,
    
    -- Match metadata
    match_rank INTEGER,  -- 1-15 ranking
    status VARCHAR(50) DEFAULT 'pending',  -- pending, contacted, meeting_scheduled, rejected
    notes TEXT,
    rejection_reason TEXT,
    
    -- Timestamps
    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    contacted_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign keys
    CONSTRAINT fk_match_client 
        FOREIGN KEY (client_profile_id) 
        REFERENCES client_upload_profiles(id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_match_prospect 
        FOREIGN KEY (prospect_id) 
        REFERENCES prospects(id) 
        ON DELETE CASCADE,
    
    -- Prevent duplicate matches
    CONSTRAINT unique_client_prospect_match 
        UNIQUE (client_profile_id, prospect_id)
);

-- Indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_matches_client_profile 
    ON client_prospect_matches(client_profile_id);

CREATE INDEX IF NOT EXISTS idx_matches_prospect 
    ON client_prospect_matches(prospect_id);

CREATE INDEX IF NOT EXISTS idx_matches_overall_score 
    ON client_prospect_matches(overall_score DESC);

CREATE INDEX IF NOT EXISTS idx_matches_status 
    ON client_prospect_matches(status);

-- ============================================
-- Table 4: Matching Runs (Optional)
-- Tracks when matching was executed
-- ============================================
CREATE TABLE IF NOT EXISTS matching_runs (
    id SERIAL PRIMARY KEY,
    run_type VARCHAR(50),  -- 'single_client', 'all_clients', 'manual'
    client_profile_id INTEGER,  -- NULL if all clients
    
    -- Run statistics
    total_clients_processed INTEGER,
    total_matches_created INTEGER,
    average_score DECIMAL(5,4),
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'running',  -- running, completed, failed
    error_message TEXT,
    
    -- Timestamps
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    
    -- Configuration used
    config JSONB,
    
    -- Foreign key (optional)
    CONSTRAINT fk_run_client 
        FOREIGN KEY (client_profile_id) 
        REFERENCES client_upload_profiles(id) 
        ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_matching_runs_status 
    ON matching_runs(status);

CREATE INDEX IF NOT EXISTS idx_matching_runs_started 
    ON matching_runs(started_at DESC);

-- ============================================
-- Trigger to update updated_at timestamps
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_client_embeddings_updated_at 
    BEFORE UPDATE ON client_embeddings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prospect_embeddings_updated_at 
    BEFORE UPDATE ON prospect_embeddings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_matches_updated_at 
    BEFORE UPDATE ON client_prospect_matches 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Verify Installation
-- ============================================
SELECT 'pgvector extension installed successfully!' AS message
WHERE EXISTS (
    SELECT 1 FROM pg_extension WHERE extname = 'vector'
);

-- Show created tables
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('client_embeddings', 'prospect_embeddings', 'client_prospect_matches', 'matching_runs')
ORDER BY tablename;