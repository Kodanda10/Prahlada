-- Migration: Add cognitive_view column to parsed_events
-- Date: 2025-11-30
-- Purpose: Support Phi 3.5 cognitive enhancement metadata

ALTER TABLE parsed_events
ADD COLUMN IF NOT EXISTS cognitive_view JSONB DEFAULT '{}'::jsonb;

COMMENT ON COLUMN parsed_events.cognitive_view IS 'Phi 3.5 cognitive analysis and reasoning for this tweet';
