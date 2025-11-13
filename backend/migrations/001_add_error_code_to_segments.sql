-- Migration: Add error_code field to segments table
-- Date: 2025-11-13
-- Description: Adds error_code column to store machine-readable error codes for failed segments

-- Add error_code column
ALTER TABLE segments ADD COLUMN IF NOT EXISTS error_code VARCHAR(100);

-- Add index for error_code for faster queries
CREATE INDEX IF NOT EXISTS idx_segments_error_code ON segments(error_code);

-- Comment the column
COMMENT ON COLUMN segments.error_code IS 'Machine-readable error code for frontend error handling';
