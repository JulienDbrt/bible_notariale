-- ChatDocAI Database Schema for Supabase Cloud
-- Run this in your Supabase SQL Editor after creating a new project

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_user BOOLEAN NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_extension VARCHAR(10) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    minio_path VARCHAR(500) NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    file_size BIGINT NOT NULL,
    indexing_status VARCHAR(20) DEFAULT 'pending' CHECK (indexing_status IN ('pending', 'indexing', 'indexed', 'failed')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'embedding', 'complete', 'failed'))
);

-- Create embedding jobs table
CREATE TABLE IF NOT EXISTS embedding_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_date ON conversations(created_date);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_upload_date ON documents(upload_date);
CREATE INDEX IF NOT EXISTS idx_embedding_jobs_status ON embedding_jobs(status);
CREATE INDEX IF NOT EXISTS idx_embedding_jobs_document_id ON embedding_jobs(document_id);

-- Create RLS policies (Row Level Security)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE embedding_jobs ENABLE ROW LEVEL SECURITY;

-- Allow all operations for authenticated users (modify for production)
CREATE POLICY "Allow all for users" ON users FOR ALL USING (true);
CREATE POLICY "Allow all for conversations" ON conversations FOR ALL USING (true);
CREATE POLICY "Allow all for messages" ON messages FOR ALL USING (true);
CREATE POLICY "Allow all for documents" ON documents FOR ALL USING (true);
CREATE POLICY "Allow all for embedding_jobs" ON embedding_jobs FOR ALL USING (true);

-- Insert seed data for development
-- Create a test user
INSERT INTO users (email, full_name) VALUES ('test@notaire.fr', 'Test Notaire') ON CONFLICT DO NOTHING;

-- Create a test conversation linked to the user
INSERT INTO conversations (user_id, title)
SELECT id, 'Conversation de test' 
FROM users 
WHERE email = 'test@notaire.fr' 
LIMIT 1
ON CONFLICT DO NOTHING;

-- Insert test message
INSERT INTO messages (conversation_id, content, is_user)
SELECT c.id, 'Bonjour ! Voici un message de test.', true 
FROM conversations c
JOIN users u ON c.user_id = u.id
WHERE u.email = 'test@notaire.fr' AND c.title = 'Conversation de test'
LIMIT 1
ON CONFLICT DO NOTHING;