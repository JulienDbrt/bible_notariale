#!/usr/bin/env python3
"""
Script pour lister tous les utilisateurs
"""
import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import get_supabase


def list_users() -> None:
    """Liste tous les utilisateurs"""
    try:
        supabase = get_supabase()

        print("🔍 Récupération de tous les utilisateurs...")
        result = supabase.table("users").select("*").execute()

        if not result.data or len(result.data) == 0:
            print("❌ Aucun utilisateur trouvé")
            return

        print(f"\n📊 {len(result.data)} utilisateur(s) trouvé(s):\n")
        print("-" * 100)

        for user in result.data:
            print(f"Email: {user['email']}")
            print(f"  - ID: {user['id']}")
            print(f"  - Nom: {user.get('full_name', 'N/A')}")
            print(f"  - Admin: {'✅ OUI' if user.get('is_admin', False) else '❌ NON'}")
            print(f"  - Créé: {user.get('created_at', 'N/A')}")
            print("-" * 100)

    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise


if __name__ == "__main__":
    list_users()
