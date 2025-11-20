"""
Script pour diagnostiquer les entités du Knowledge Graph
"""
import asyncio
from src.services.neo4j_service import get_neo4j_service

async def diagnose_entities():
    """Examiner la structure des entités dans Neo4j"""
    neo4j = get_neo4j_service()
    await neo4j.initialize()

    print("=" * 80)
    print("DIAGNOSTIC: Structure des entités Neo4j")
    print("=" * 80)

    if not neo4j.driver:
        print("❌ Driver Neo4j non initialisé")
        return

    async with neo4j.driver.session() as session:
        # Récupérer quelques entités pour voir leur structure
        result = await session.run("""
            MATCH (e)
            WHERE NOT e:Chunk AND NOT e:Document
            WITH e, labels(e) as nodeLabels
            RETURN
                labels(e) as labels,
                properties(e) as props,
                count{(e)-[]->()} + count{(e)<-[]-()} as degree
            ORDER BY degree DESC
            LIMIT 10
        """)

        print("\n📊 Échantillon d'entités (10 plus connectées):\n")

        entities = []
        async for record in result:
            entities.append({
                "labels": record["labels"],
                "props": dict(record["props"]),
                "degree": record["degree"]
            })

        for i, entity in enumerate(entities, 1):
            print(f"\nEntité {i}:")
            print(f"  Labels: {entity['labels']}")
            print(f"  Degree (connexions): {entity['degree']}")
            print(f"  Propriétés disponibles: {list(entity['props'].keys())}")
            print(f"  Valeurs:")
            for key, value in entity['props'].items():
                # Tronquer les valeurs longues
                if isinstance(value, str) and len(value) > 100:
                    print(f"    {key}: {value[:100]}...")
                else:
                    print(f"    {key}: {value}")

        # Statistiques sur les propriétés disponibles
        print("\n" + "=" * 80)
        print("📈 STATISTIQUES SUR LES PROPRIÉTÉS")
        print("=" * 80)

        stats_result = await session.run("""
            MATCH (e)
            WHERE NOT e:Chunk AND NOT e:Document
            WITH e
            WHERE exists(e.name) OR exists(e.value) OR exists(e.text)
            RETURN
                count(CASE WHEN exists(e.name) THEN 1 END) as has_name,
                count(CASE WHEN exists(e.value) THEN 1 END) as has_value,
                count(CASE WHEN exists(e.text) THEN 1 END) as has_text,
                count(e) as total
        """)

        async for record in stats_result:
            total = record["total"]
            print(f"\n  Total entités avec au moins une propriété utile: {total}")
            print(f"  - Avec propriété 'name': {record['has_name']}")
            print(f"  - Avec propriété 'value': {record['has_value']}")
            print(f"  - Avec propriété 'text': {record['has_text']}")

        # Compter les entités SANS propriété utile
        no_props_result = await session.run("""
            MATCH (e)
            WHERE NOT e:Chunk AND NOT e:Document
            WITH e
            WHERE NOT exists(e.name) AND NOT exists(e.value) AND NOT exists(e.text)
            RETURN count(e) as no_useful_props
        """)

        async for record in no_props_result:
            print(f"\n  ⚠️  Entités SANS propriété utile: {record['no_useful_props']}")
            if record['no_useful_props'] > 0:
                print("     Ces entités utiliseront le fallback 'Entity_ID'")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(diagnose_entities())
