-- Add citations field to messages to store document references per message

ALTER TABLE messages 
ADD COLUMN IF NOT EXISTS citations JSONB;

COMMENT ON COLUMN messages.citations IS 'Array of citation objects: [{documentId, title, page, score, snippet}]';

