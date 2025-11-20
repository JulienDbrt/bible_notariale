-- Script pour peupler les colonnes manquantes avec les données des conversations
-- À exécuter APRÈS update_evaluations_table_v2.sql

-- Mise à jour des evaluations existantes pour récupérer question et response
-- depuis les messages de conversation correspondants
UPDATE evaluations e
SET 
    question = (
        SELECT m.content 
        FROM messages m 
        WHERE m.conversation_id = e.conversation_id 
        AND m.role = 'user'
        ORDER BY m.created_at DESC 
        LIMIT 1
    ),
    response = (
        SELECT m.content 
        FROM messages m 
        WHERE m.id = e.message_id
    ),
    sources = (
        SELECT m.sources 
        FROM messages m 
        WHERE m.id = e.message_id
    )
WHERE e.question IS NULL OR e.response IS NULL;

-- Marquer toutes les evaluations existantes comme non traitées 
-- pour qu'elles soient analysées par l'agent
UPDATE evaluations 
SET processed = FALSE 
WHERE processed IS NULL;

-- Afficher les statistiques de migration
DO $$
DECLARE
    total_count INTEGER;
    negative_count INTEGER;
    to_process_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_count FROM evaluations;
    SELECT COUNT(*) INTO negative_count FROM evaluations WHERE feedback = 'negative';
    SELECT COUNT(*) INTO to_process_count FROM evaluations WHERE feedback = 'negative' AND processed = FALSE;
    
    RAISE NOTICE 'Migration terminée:';
    RAISE NOTICE '  - Total evaluations: %', total_count;
    RAISE NOTICE '  - Feedbacks négatifs: %', negative_count;
    RAISE NOTICE '  - À traiter par l''agent: %', to_process_count;
END $$;