-- Ajout de la colonne is_admin à la table users
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;

-- Index pour optimiser les requêtes sur is_admin
CREATE INDEX IF NOT EXISTS idx_users_is_admin ON users(is_admin);

-- Commentaire pour documentation
COMMENT ON COLUMN users.is_admin IS 'Flag binaire pour l''accès administrateur/tribunal';