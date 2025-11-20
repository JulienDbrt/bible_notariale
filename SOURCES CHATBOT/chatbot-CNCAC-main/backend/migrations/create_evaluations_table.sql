-- Create evaluations table for user feedback on chat responses
CREATE TABLE IF NOT EXISTS evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    message_id UUID NOT NULL, -- Reference to the specific message being evaluated
    user_id UUID NOT NULL,
    evaluation_type VARCHAR(10) NOT NULL CHECK (evaluation_type IN ('positive', 'negative')),
    comment TEXT, -- Optional comment, mandatory if evaluation_type is 'negative'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT evaluations_negative_comment_required 
        CHECK (evaluation_type = 'positive' OR (evaluation_type = 'negative' AND comment IS NOT NULL AND length(trim(comment)) > 0))
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS evaluations_conversation_id_idx ON evaluations(conversation_id);
CREATE INDEX IF NOT EXISTS evaluations_user_id_idx ON evaluations(user_id);
CREATE INDEX IF NOT EXISTS evaluations_message_id_idx ON evaluations(message_id);
CREATE INDEX IF NOT EXISTS evaluations_type_idx ON evaluations(evaluation_type);
CREATE INDEX IF NOT EXISTS evaluations_created_at_idx ON evaluations(created_at DESC);

-- Unique constraint to prevent duplicate evaluations for the same message
CREATE UNIQUE INDEX IF NOT EXISTS evaluations_unique_message_user 
    ON evaluations(message_id, user_id);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_evaluations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_evaluations_updated_at ON evaluations;
CREATE TRIGGER update_evaluations_updated_at
    BEFORE UPDATE ON evaluations
    FOR EACH ROW
    EXECUTE FUNCTION update_evaluations_updated_at();