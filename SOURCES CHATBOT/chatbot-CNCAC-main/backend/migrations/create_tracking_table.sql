-- Migration: Création de la table de tracking pour l'ingestion de documents

CREATE TABLE IF NOT EXISTS document_ingestion_status (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    filename TEXT UNIQUE NOT NULL,
    file_hash TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'processing', 'success', 'failed', 'invalid', 'error')),
    last_processed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    document_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour les recherches fréquentes
CREATE INDEX idx_ingestion_status_filename ON document_ingestion_status(filename);
CREATE INDEX idx_ingestion_status_hash ON document_ingestion_status(file_hash);
CREATE INDEX idx_ingestion_status_status ON document_ingestion_status(status);
CREATE INDEX idx_ingestion_status_processed ON document_ingestion_status(last_processed DESC);

-- Trigger pour mise à jour automatique de updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_document_ingestion_status_updated_at 
    BEFORE UPDATE ON document_ingestion_status 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS)
ALTER TABLE document_ingestion_status ENABLE ROW LEVEL SECURITY;

-- Politique pour les utilisateurs authentifiés (lecture seule pour l'instant)
CREATE POLICY "Users can view ingestion status" 
    ON document_ingestion_status
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Politique pour le service backend (toutes opérations)
CREATE POLICY "Service account full access" 
    ON document_ingestion_status
    FOR ALL
    USING (auth.role() = 'service_role');

-- Vue pour les statistiques d'ingestion
CREATE OR REPLACE VIEW ingestion_statistics AS
SELECT 
    status,
    COUNT(*) as document_count,
    MAX(last_processed) as last_activity,
    AVG((metadata->>'extraction_time')::float) as avg_extraction_time,
    AVG((metadata->>'ingest_time')::float) as avg_ingest_time,
    SUM((metadata->>'text_length')::int) as total_text_processed
FROM document_ingestion_status
GROUP BY status;

-- Vue pour les documents problématiques
CREATE OR REPLACE VIEW problematic_documents AS
SELECT 
    filename,
    status,
    error_message,
    metadata->>'document_type' as document_type,
    last_processed
FROM document_ingestion_status
WHERE status IN ('failed', 'invalid', 'error')
ORDER BY last_processed DESC;

COMMENT ON TABLE document_ingestion_status IS 'Tracking de l''ingestion des documents pour le système RAG NotariaCore';
COMMENT ON COLUMN document_ingestion_status.file_hash IS 'Hash SHA256 du contenu du fichier pour déduplication';
COMMENT ON COLUMN document_ingestion_status.metadata IS 'Métadonnées extraites : type, pages, tables, temps de traitement, etc.';