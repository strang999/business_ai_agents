-- ============================================
-- AI LIFE COACH: SUPABASE SCHEMA (ENHANCED)
-- Pavel Bilskiy "SelfMade Man" Methodology
-- Run this in Supabase SQL Editor
-- ============================================

-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create 'memories' table for RAG knowledge base (Enhanced with tags)
CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI text-embedding-3-small
    source TEXT,             -- e.g., "session_2_drivers.txt"
    user_id TEXT,            -- NULL for global knowledge
    -- Enhanced Metadata for Pavel Bilskiy Methodology
    concept TEXT,            -- "diagnostic", "injunction", "practice", "tool", "theory"
    session_number INT,      -- 1-6 (course session)
    driver_target TEXT,      -- "be_strong", "be_best", "please_others", "all"
    script_pattern TEXT,     -- "until", "after", "never", "always", "all"
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Create index for fast similarity search
CREATE INDEX IF NOT EXISTS memories_embedding_idx 
ON memories 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 4. Create 'profiles' table with ENHANCED diagnosis data
CREATE TABLE IF NOT EXISTS profiles (
    id TEXT PRIMARY KEY,  -- user_id
    -- Psychological Profile (from Onboarding)
    diagnosis_data JSONB DEFAULT '{
        "driver": null,
        "driver_score": {"be_strong": 0, "be_best": 0, "please_others": 0},
        "script_pattern": null,
        "core_wound": null,
        "injunctions": [],
        "onboarding_completed": false,
        "awareness_streak": 0
    }'::jsonb,
    -- Semantic Memory (facts about user)
    psychological_data JSONB DEFAULT '{}'::jsonb,
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Create 'awareness_journal' table for daily logs
CREATE TABLE IF NOT EXISTS awareness_journal (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL REFERENCES profiles(id),
    event_description TEXT NOT NULL,
    negative_interpretation TEXT,
    healthy_interpretation TEXT,
    emotion_before TEXT,
    emotion_after TEXT,
    driver_triggered TEXT,  -- Which driver was activated
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Enhanced function for similarity search with filtering
CREATE OR REPLACE FUNCTION match_memories_enhanced(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5,
    filter_user_id TEXT DEFAULT NULL,
    filter_driver TEXT DEFAULT NULL,
    filter_concept TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    source TEXT,
    concept TEXT,
    driver_target TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.content,
        m.source,
        m.concept,
        m.driver_target,
        1 - (m.embedding <=> query_embedding) AS similarity
    FROM memories m
    WHERE 
        -- User filter
        (filter_user_id IS NULL AND m.user_id IS NULL) OR m.user_id = filter_user_id
        -- Driver filter (match specific or "all")
        AND (filter_driver IS NULL OR m.driver_target = filter_driver OR m.driver_target = 'all')
        -- Concept filter
        AND (filter_concept IS NULL OR m.concept = filter_concept)
    ORDER BY m.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 7. Function to update profile diagnosis
CREATE OR REPLACE FUNCTION update_diagnosis(
    p_user_id TEXT,
    p_diagnosis JSONB
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO profiles (id, diagnosis_data, updated_at)
    VALUES (p_user_id, p_diagnosis, NOW())
    ON CONFLICT (id) DO UPDATE
    SET 
        diagnosis_data = p_diagnosis,
        updated_at = NOW();
END;
$$;

-- 8. Function to upsert profile data (Semantic Memory)
CREATE OR REPLACE FUNCTION upsert_profile(
    p_user_id TEXT,
    p_data JSONB
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO profiles (id, psychological_data, updated_at)
    VALUES (p_user_id, p_data, NOW())
    ON CONFLICT (id) DO UPDATE
    SET 
        psychological_data = profiles.psychological_data || p_data,
        updated_at = NOW();
END;
$$;
