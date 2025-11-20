"""
Script pour vérifier si les citations sont présentes dans une conversation Supabase
"""
import asyncio
from dotenv import load_dotenv
from src.core.database import get_supabase_client

load_dotenv()

async def check_conversation():
    """Vérifier les citations dans la conversation de test"""
    supabase = get_supabase_client()

    conversation_id = "21bc4d81-f018-4b7f-813d-fa4ff2135fc4"

    print("=" * 80)
    print(f"Vérification de la conversation: {conversation_id}")
    print("=" * 80)

    try:
        # Récupérer les messages de la conversation
        result = supabase.table("messages") \
            .select("id, content, is_user, timestamp, citations") \
            .eq("conversation_id", conversation_id) \
            .order("timestamp", desc=False) \
            .execute()

        if not result.data:
            print("\n❌ Aucun message trouvé pour cette conversation")
            return

        print(f"\n📝 {len(result.data)} messages trouvés:\n")

        for i, msg in enumerate(result.data):
            role = "👤 Utilisateur" if msg["is_user"] else "🤖 Assistant"
            timestamp = msg["timestamp"]
            content_preview = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]

            print(f"\nMessage {i+1} - {role} ({timestamp}):")
            print(f"  Contenu: {content_preview}")

            if not msg["is_user"]:
                citations = msg.get("citations")
                if citations:
                    print(f"  ✅ Citations: {len(citations)} trouvée(s)")
                    for j, citation in enumerate(citations):
                        print(f"    {j+1}. Document: {citation.get('documentPath', 'N/A')}")
                else:
                    print(f"  ⚠️  Aucune citation enregistrée")

        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\n❌ Erreur lors de la récupération: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_conversation())
