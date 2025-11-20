#!/usr/bin/env python3
"""
Script pour rendre un utilisateur administrateur
Usage: python scripts/make_user_admin.py <email>
"""
import sys
import asyncio
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import get_supabase


def make_user_admin(email: str) -> None:
    """Rend un utilisateur administrateur"""
    try:
        supabase = get_supabase()

        # Rechercher l'utilisateur par email
        print(f"🔍 Recherche de l'utilisateur: {email}")
        result = supabase.table("users").select("*").eq("email", email).execute()

        if not result.data or len(result.data) == 0:
            print(f"❌ Utilisateur non trouvé: {email}")
            print("\n💡 L'utilisateur doit d'abord créer un compte sur l'application.")
            return

        user = result.data[0]
        print(f"✅ Utilisateur trouvé: {user['email']} (ID: {user['id']})")
        print(f"   - Nom: {user.get('full_name', 'N/A')}")
        print(f"   - Admin actuel: {user.get('is_admin', False)}")

        # Mettre à jour le statut admin
        print(f"\n🔧 Mise à jour du statut admin...")
        update_result = supabase.table("users").update({
            "is_admin": True
        }).eq("id", user["id"]).execute()

        if update_result.data:
            print(f"✅ {email} est maintenant administrateur !")
            print(f"\n📊 Nouvelles permissions:")
            print(f"   - Accès administrateur: ✅")
            print(f"   - Accès aux évaluations: ✅")
            print(f"   - Accès au dashboard admin: ✅")
        else:
            print(f"❌ Échec de la mise à jour")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/make_user_admin.py <email>")
        print("Exemple: python scripts/make_user_admin.py frederic.ramet@example.com")
        sys.exit(1)

    email = sys.argv[1]
    make_user_admin(email)
