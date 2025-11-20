-- Add admin workflow columns to evaluations table
-- Safe to run multiple times thanks to IF NOT EXISTS

ALTER TABLE evaluations 
ADD COLUMN IF NOT EXISTS processed_by UUID REFERENCES users(id);

CREATE INDEX IF NOT EXISTS evaluations_processed_by_idx 
  ON evaluations(processed_by);

ALTER TABLE evaluations 
ADD COLUMN IF NOT EXISTS rejected BOOLEAN DEFAULT FALSE;

ALTER TABLE evaluations 
ADD COLUMN IF NOT EXISTS rejection_reason TEXT;

COMMENT ON COLUMN evaluations.processed_by IS 'User ID of the admin who processed the evaluation';
COMMENT ON COLUMN evaluations.rejected IS 'Whether the evaluation was rejected by admin review';
COMMENT ON COLUMN evaluations.rejection_reason IS 'Optional reason provided when rejecting';

