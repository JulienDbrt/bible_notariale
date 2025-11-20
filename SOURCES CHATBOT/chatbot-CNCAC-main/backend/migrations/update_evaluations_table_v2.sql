-- Migration pour ajouter les colonnes manquantes à la table evaluations
-- Nécessaire pour le fonctionnement de l'agent d'amélioration automatique

-- Ajouter la colonne 'question' qui contient la question posée par l'utilisateur
ALTER TABLE evaluations 
ADD COLUMN IF NOT EXISTS question TEXT;

-- Ajouter la colonne 'response' qui contient la réponse de l'IA évaluée
ALTER TABLE evaluations 
ADD COLUMN IF NOT EXISTS response TEXT;

-- Ajouter la colonne 'sources' pour stocker les citations utilisées
ALTER TABLE evaluations 
ADD COLUMN IF NOT EXISTS sources JSONB;

-- Ajouter la colonne 'processed' pour tracker le traitement par l'agent
ALTER TABLE evaluations 
ADD COLUMN IF NOT EXISTS processed BOOLEAN DEFAULT FALSE;

-- Ajouter la colonne 'processed_at' pour horodater le traitement
ALTER TABLE evaluations 
ADD COLUMN IF NOT EXISTS processed_at TIMESTAMP WITH TIME ZONE;

-- Renommer 'evaluation_type' en 'feedback' pour correspondre au code de l'agent
-- D'abord vérifier si la colonne evaluation_type existe et feedback n'existe pas
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'evaluations' 
               AND column_name = 'evaluation_type')
    AND NOT EXISTS (SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'evaluations' 
                    AND column_name = 'feedback') THEN
        ALTER TABLE evaluations RENAME COLUMN evaluation_type TO feedback;
    END IF;
END $$;

-- Créer un index sur la colonne 'processed' pour optimiser les requêtes de l'agent
CREATE INDEX IF NOT EXISTS evaluations_processed_idx ON evaluations(processed) 
WHERE processed = FALSE;

-- Créer un index sur 'feedback' pour les requêtes de feedbacks négatifs
CREATE INDEX IF NOT EXISTS evaluations_feedback_idx ON evaluations(feedback) 
WHERE feedback = 'negative';

-- Mettre à jour la contrainte de vérification si nécessaire
ALTER TABLE evaluations DROP CONSTRAINT IF EXISTS evaluations_negative_comment_required;
ALTER TABLE evaluations ADD CONSTRAINT evaluations_negative_comment_required 
    CHECK (feedback = 'positive' OR (feedback = 'negative' AND comment IS NOT NULL AND length(trim(comment)) > 0));

-- Commentaire pour documenter les changements
COMMENT ON COLUMN evaluations.question IS 'Question posée par l''utilisateur lors de la conversation';
COMMENT ON COLUMN evaluations.response IS 'Réponse de l''IA qui a été évaluée';
COMMENT ON COLUMN evaluations.sources IS 'Sources et citations utilisées dans la réponse (format JSON)';
COMMENT ON COLUMN evaluations.processed IS 'Indique si le feedback a été traité par l''agent d''amélioration';
COMMENT ON COLUMN evaluations.processed_at IS 'Date et heure du traitement par l''agent';
COMMENT ON COLUMN evaluations.feedback IS 'Type de feedback: positive ou negative (renommé depuis evaluation_type)';