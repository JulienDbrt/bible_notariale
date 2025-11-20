# Documentation RAG & Graph RAG 



**Version**: PROTOCOLE DAN v5

**Audience**: Développeurs, Product Owners, Architectes

**Dernière mise à jour**: Novembre 2025

***

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Architecture du système RAG](#2-architecture-du-système-rag)
3. [Pipeline d'ingestion des documents](#3-pipeline-dingestion-des-documents)
4. [PROTOCOLE DAN v5 - Agent ReAct](#4-protocole-dan-v5---agent-react)
5. [Stratégies de recherche (Legacy)](#5-stratégies-de-recherche-legacy)
6. [Graph RAG - Exploitation du graphe de connaissances](#6-graph-rag---exploitation-du-graphe-de-connaissances)
7. [Configuration et paramétrage](#7-configuration-et-paramétrage)
8. [Exemples d'utilisation](#8-exemples-dutilisation)
9. [Métriques et monitoring](#9-métriques-et-monitoring)
10. [Pistes d'évolution et roadmap](#10-pistes-dévolution-et-roadmap)

***

## 1. Vue d'ensemble

### 1.1 Qu'est-ce qu'un RAG ?

**RAG (Retrieval-Augmented Generation)** est une architecture qui combine :

* **Retrieval** (Recherche) : Trouver les documents/passages pertinents dans une base de connaissances
* **Augmentation** : Enrichir le contexte avec ces informations
* **Generation** : Générer une réponse via un LLM en utilisant ce contexte enrichi

### 1.2 Notre approche : Graph RAG Hybride

ChatDocAI utilise une approche **hybride innovante** qui combine :

```
┌─────────────────────────────────────────────────────────────┐
│                     GRAPH RAG HYBRIDE                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🔍 RECHERCHE VECTORIELLE    +    🕸️ GRAPHE DE              │
│     (Similarité sémantique)        CONNAISSANCES            │
│                                    (Relations entre entités) │
│                                                              │
│  📊 FULL-TEXT SEARCH         +    🧠 AGENT ReAct            │
│     (Recherche lexicale)           (Raisonnement cognitif)  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Avantages de cette architecture** :

* ✅ **Précision** : Combine la recherche sémantique et lexicale
* ✅ **Contexte** : Exploite les relations entre entités (Graph RAG)
* ✅ **Intelligence** : Agent capable de raisonner et résoudre les coréférences
* ✅ **Traçabilité** : Citations précises avec références aux documents sources
* ✅ **Flexibilité** : Multiples stratégies selon le type de question

### 1.3 Stack technique

| Composant                  | Technologie                           | Rôle                                      |
| -------------------------- | ------------------------------------- | ----------------------------------------- |
| **Base de données graphe** | Neo4j                                 | Stockage des vecteurs, entités, relations |
| **Embeddings**             | OpenAI (text-embedding-3-small/large) | Conversion texte → vecteurs               |
| **LLM Extraction**         | gpt-4.1-mini-2025-04-14               | Extraction d'entités et relations         |
| **LLM Planning**           | gpt-4.1-nano-2025-04-14               | Raisonnement et planification             |
| **LLM Synthesis**          | gpt-4.1-2025-04-14                    | Génération de réponses                    |
| **Parsing**                | Docling + PyMuPDF                     | Extraction de texte multi-format          |
| **Storage**                | MinIO + Supabase                      | Documents bruts + métadonnées             |

***

## 2. Architecture du système RAG

### 2.1 Schéma d'architecture global

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER QUESTION                             │
│                  "Quelle est la franchise aggravée ?"            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROTOCOLE DAN v5                              │
│                   (Agent ReAct)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [1] REASON 🧠                                                   │
│      ├─ Analyse la question                                     │
│      ├─ Résout les coréférences (historique conversationnel)    │
│      ├─ Identifie les synonymes juridiques                      │
│      └─ Formule une requête optimisée                           │
│           ↓                                                      │
│  [2] ACT 🎯                                                      │
│      ├─ Recherche VECTORIELLE (embedding → Neo4j)               │
│      ├─ Recherche FULL-TEXT (mots-clés → Lucene)                │
│      ├─ FUSION des résultats (déduplication)                    │
│      └─ RERANKING intelligent (LLM évalue pertinence)           │
│           ↓                                                      │
│  [3] OBSERVE 📝                                                  │
│      ├─ Synthèse de la réponse (gpt-4.1)                        │
│      ├─ Extraction des citations [Passage X]                    │
│      └─ Formatage final                                         │
│                                                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI RESPONSE + CITATIONS                       │
│  "La franchise aggravée est un dispositif... [Passage 1]"       │
│                                                                  │
│  Sources: 3 passages sources • 2 documents                      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Composants clés

#### 2.2.1 Service RAG (`backend/src/services/notaria_rag_service.py`)

**Responsabilités** :

* Orchestration de l'agent ReAct
* Génération d'embeddings
* Extraction d'entités via LLM
* Synthèse des réponses avec citations
* Gestion de la mémoire conversationnelle

**Points d'entrée principaux** :

```python
# PROTOCOLE DAN v5 - Méthode principale
async def query(question: str, conversation_history: Optional[List]) -> Dict[str, Any]

# Legacy - Avec métriques
async def query_with_metrics(question: str) -> Dict[str, Any]

# Ingestion
async def ingest_raw_document(document_id: str, file_path: str, text_content: str) -> bool
```

#### 2.2.2 Service Neo4j (`backend/src/services/neo4j_service.py`)

**Responsabilités** :

* Gestion de la connexion Neo4j
* Indexation vectorielle (cosine similarity)
* Indexation full-text (Lucene)
* Requêtes Cypher pour le graphe
* Stockage des entités et relations

**Méthodes clés** :

```python
# Recherche vectorielle
async def search_chunks_by_vector(embedding: List[float], limit: int) -> List[Dict]

# Recherche full-text
async def search_chunks_by_fulltext(query: str, limit: int) -> List[Dict]

# Exploration du graphe
async def find_paths_between_entities(entity_names: List[str], max_depth: int) -> List[str]

# Enrichissement contextuel
async def get_relations_from_chunks(chunk_ids: List[str], limit: int) -> List[Dict]

# Visualisation
async def get_knowledge_graph(limit: int) -> Dict[str, Any]
```

***

## 3. Pipeline d'ingestion des documents

### 3.1 Vue d'ensemble du pipeline

Le pipeline transforme un document brut en une base de connaissances structurée et interrogeable.

```
┌──────────────┐
│ Document PDF │
│   (MinIO)    │
└──────┬───────┘
       │
       ▼
┌────────────────────────────────────────────────────────────┐
│ ÉTAPE 1: PARSING                                           │
├────────────────────────────────────────────────────────────┤
│ • PyMuPDF (rapide) pour PDFs textuels                      │
│ • Docling + OCR pour PDFs scannés ou autres formats       │
│ • Support: PDF, DOCX, TXT, MD, EML, HTML, PPT, XLS, etc.  │
└────────────────────────┬───────────────────────────────────┘
                         │ Texte extrait
                         ▼
┌────────────────────────────────────────────────────────────┐
│ ÉTAPE 2: CHUNKING SÉMANTIQUE                               │
├────────────────────────────────────────────────────────────┤
│ • Découpage en chunks de 512 tokens                        │
│ • Respect des paragraphes comme unités sémantiques         │
│ • Overlap de 50 tokens pour la cohérence                   │
└────────────────────────┬───────────────────────────────────┘
                         │ Liste de chunks
                         ▼
┌────────────────────────────────────────────────────────────┐
│ ÉTAPE 3: ANALYSE SÉMANTIQUE (LLM)                          │
├────────────────────────────────────────────────────────────┤
│ • Extraction d'entités (Personnes, Orgs, Concepts, etc.)  │
│ • Extraction de relations (EST_UN_TYPE_DE, etc.)          │
│ • Large chunks (60K tokens) pour l'analyse globale        │
│ • LLM: gpt-4.1-mini avec prompt spécialisé notarial       │
└────────────┬───────────────────────────────┬───────────────┘
             │ Entités + Relations          │ Chunks
             ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│ ÉTAPE 4a: EMBEDDING      │    │ ÉTAPE 4b: GRAPH STORAGE  │
├──────────────────────────┤    ├──────────────────────────┤
│ • text-embedding-3-small │    │ • Création des nœuds     │
│ • 1536 dimensions        │    │   Entity, Document       │
│ • Batch processing       │    │ • Création des relations │
│ • OpenAI API             │    │ • Labels typés           │
└──────────┬───────────────┘    └──────────┬───────────────┘
           │                               │
           └───────────┬───────────────────┘
                       ▼
┌────────────────────────────────────────────────────────────┐
│ ÉTAPE 5: INDEXATION NEO4J                                  │
├────────────────────────────────────────────────────────────┤
│ • Index vectoriel (cosine similarity)                      │
│ • Index full-text (Lucene)                                 │
│ • Nœuds: Chunk → Document                                  │
│ • Relations: BELONGS_TO, MENTIONED_IN, etc.                │
└────────────────────────────────────────────────────────────┘
```

### 3.2 Code d'ingestion simplifié

**Fichier**: `backend/scripts/ingestion_pipeline.py`

```python
# Traitement parallèle avec concurrence contrôlée
CONCURRENCY_LIMIT = 2  # Nombre de documents traités simultanément

# Parsing adaptatif selon le format
if file_extension == '.eml':
    text, metadata = self._parse_eml_file(filename, content)
elif file_extension == '.pdf':
    # Tentative rapide avec PyMuPDF
    text = extract_with_pymupdf(content)
    if len(text) < MIN_CONTENT_LENGTH:
        # Fallback sur Docling avec OCR
        text = self._extract_text_with_docling(filename, content)
else:
    # Autres formats → Docling directement
    text = self._extract_text_with_docling(filename, content)

# Envoi au service RAG pour analyse complète
success = await rag_service.ingest_raw_document(
    document_id=filename,
    file_path=filename,
    text_content=text
)
```

### 3.3 Stratégie de chunking

Le chunking est **sémantiquement conscient** :

```python
# 1. Respect des paragraphes
paragraphs = text.split('\n\n')

# 2. Segmentation par phrases
sentences = re.split(r'(?<=[.!?])\s+', paragraph)

# 3. Agrégation jusqu'à 512 tokens
current_chunk_tokens = []
for tokens in sentence_tokens:
    if len(current_chunk_tokens) + len(tokens) > 512:
        # Finaliser le chunk
        chunks.append(decode(current_chunk_tokens))

        # 4. Overlap de 50 tokens pour cohérence
        overlap_start = max(0, len(current_chunk_tokens) - 50)
        current_chunk_tokens = current_chunk_tokens[overlap_start:]

    current_chunk_tokens.extend(tokens)
```

**Pourquoi 512 tokens ?**

* ✅ Suffisamment large pour capturer le contexte
* ✅ Assez petit pour précision de la recherche
* ✅ Compatible avec les limites d'embedding
* ✅ Équilibre performance/coût

### 3.4 Extraction d'entités et relations

Le LLM reçoit un **prompt spécialisé notarial** :

```
Tu es un expert en modélisation de connaissance pour le domaine notarial français.
Extrais TOUTES les entités et relations pertinentes.

TYPES D'ENTITÉS :
- Personne: "Me Romain Lecordier", "Eric Dupond-Moretti"
- Organisation: "MMA IARD", "Conseil Supérieur du Notariat"
- ConceptJuridique: "franchise aggravée", "société multi-offices (SMO)"
- Document: "contrat n° 145 154 406", "décret 2024-906"
- Date: "1er janvier 2025"
- Lieu: "Basse-Normandie", "Caen"

TYPES DE RELATIONS :
- EST_UN_TYPE_DE
- S_APPLIQUE_A
- A_POUR_REGLE
- MEMBRE_DE
- SITUÉ_À
- A_POUR_DATE_DEFFET
```

**Résultat** : Un graphe de connaissances structuré dans Neo4j.

***

## 4. PROTOCOLE DAN v5 - Agent ReAct

### 4.1 Qu'est-ce que ReAct ?

**ReAct** = **Rea**soning + **Act**ing

Architecture cognitive qui simule le raisonnement humain :

1. **Penser** (Reason) → Analyser le problème
2. **Agir** (Act) → Exécuter des actions
3. **Observer** (Observe) → Évaluer les résultats

### 4.2 Implémentation dans ChatDocAI

```python
async def query(question: str, conversation_history: Optional[List]) -> Dict:
    """
    PROTOCOLE DAN v5 - Agent ReAct avec mémoire conversationnelle
    """

    # ─────────────────────────────────────────────────────────
    # ÉTAPE 1: RAISONNEMENT (REASON)
    # ─────────────────────────────────────────────────────────
    thought_process = await self._reasoning_step(question, conversation_history)
    search_query = thought_process["search_query"]

    # L'agent analyse:
    # ✓ Le contexte conversationnel (10 derniers messages)
    # ✓ Les coréférences ("cette négociation" → sujet réel)
    # ✓ Les synonymes juridiques ("recours" → "réclamation, médiateur")
    # ✓ Les termes exacts à rechercher

    # ─────────────────────────────────────────────────────────
    # ÉTAPE 2: ACTION (ACT)
    # ─────────────────────────────────────────────────────────
    context_chunks = await self._hybrid_search_step(search_query)

    # L'agent exécute:
    # ✓ Recherche vectorielle (similarité sémantique)
    # ✓ Recherche full-text (mots-clés exacts)
    # ✓ Fusion et déduplication
    # ✓ Reranking intelligent (LLM évalue la pertinence)

    # ─────────────────────────────────────────────────────────
    # ÉTAPE 3: OBSERVATION & SYNTHÈSE (OBSERVE)
    # ─────────────────────────────────────────────────────────
    return await self._synthesize_answer_with_citations(question, context_chunks)

    # L'agent génère:
    # ✓ Réponse nuancée basée sur les chunks
    # ✓ Citations précises [Passage X]
    # ✓ Gestion de l'incertitude
```

### 4.3 Étape REASON - Résolution de coréférences

**Exemple concret** :

```
Historique conversationnel:
  User: "Quelles sont les règles pour une négociation immobilière ?"
  AI: "Une négociation immobilière nécessite un mandat écrit..."

Question actuelle:
  User: "Y a-t-il des limites ?"

┌─────────────────────────────────────────────────────────┐
│ AGENT REASONING (LLM nano)                              │
├─────────────────────────────────────────────────────────┤
│ Thought:                                                │
│ "L'utilisateur demande 'y a-t-il des limites' mais     │
│  ne précise pas de quoi. En analysant l'historique,    │
│  le sujet est 'négociation immobilière'. Je dois donc   │
│  résoudre la coréférence."                              │
│                                                         │
│ Search Query:                                           │
│ "limites négociation immobilière notaire déontologie   │
│  mandat durée montant"                                  │
└─────────────────────────────────────────────────────────┘
```

### 4.4 Étape ACT - Recherche hybride

```python
async def _hybrid_search_step(search_query: str) -> List[Dict]:
    # 1. Génération de l'embedding
    vector_embedding = await self._get_embeddings([search_query])

    # 2. Recherche parallèle
    vector_results, fulltext_results = await asyncio.gather(
        neo4j.search_chunks_by_vector(vector_embedding[0], limit=7),
        neo4j.search_chunks_by_fulltext(search_query, limit=7)
    )

    # 3. Fusion et déduplication
    all_chunks = {chunk['chunkId']: chunk for chunk in vector_results}
    for chunk in fulltext_results:
        if chunk['chunkId'] not in all_chunks:
            all_chunks[chunk['chunkId']] = chunk

    # 4. Reranking LLM
    reranked = await self._rerank_chunks(search_query, list(all_chunks.values()))

    # 5. Sélection finale
    return reranked[:5]  # Top 5 chunks
```

**Pourquoi le reranking ?**

La similarité vectorielle ne garantit pas la pertinence réelle. Le LLM évalue :

* Le chunk contient-il **vraiment** la réponse ?
* Quelle est la **qualité** de l'information ?
* Le contexte est-il **complet** ?

```python
# Prompt de reranking
"""
Pour chaque passage, évalue sa pertinence sur une échelle de 0 à 10:
- 10: Contient directement la réponse
- 7-9: Très pertinent et lié
- 4-6: Contexte partiel
- 1-3: Faiblement lié
- 0: Non pertinent

Question: "Quelle est la franchise aggravée ?"

Passages:
--- Passage 0 ---
La franchise aggravée est un dispositif qui porte la franchise à
5 fois son montant initial en cas de sinistre de mauvaise foi...

--- Passage 1 ---
Le contrat d'assurance MMA IARD couvre les risques cyber...

Réponse: {"scores": [{"passage": 0, "score": 10}, {"passage": 1, "score": 2}]}
```

### 4.5 Étape OBSERVE - Synthèse avec citations

Le prompt de synthèse intègre une **gestion nuancée de l'incertitude** :

```
Tu es un assistant notarial expert. Réponds en te basant EXCLUSIVEMENT
sur les passages fournis.

DIRECTIVES :

1. Réponse claire → Fournis-la avec citations [Passage X]

2. Réponse partielle → Ne dis PAS "information non disponible"
   - Fournis ce que tu as trouvé
   - Indique ce qui manque
   - Invite à préciser
   Exemple: "Les documents mentionnent les franchises pour la fraude
   informatique [Passage 2], mais ne spécifient pas l'option 8.
   Pourriez-vous préciser le type de contrat ?"

3. Aucune information → Formule nuancée
   "Je n'ai pas trouvé d'information précise. Serait-il possible de
   reformuler ou d'apporter plus de détails ?"

PASSAGES EXTRAITS:
[Passage 1 - Document: contrat_mma.pdf]
La franchise aggravée est un dispositif...
```

**Extraction automatique des citations** :

```python
# Regex pour trouver les [Passage X]
passage_indices = re.findall(r'\[Passage (\d+)\]', answer)

# Construction de la liste de citations
for index in unique_indices:
    chunk = context_chunks[index]
    citations.append({
        "documentId": chunk['documentId'],
        "documentPath": chunk['documentPath'],
        "text": chunk['text']
    })

# Nettoyage de la réponse
cleaned_answer = re.sub(r'\s*\[Passage \d+\]', '', answer)
```

***

## 5. Stratégies de recherche (Legacy)

**Note**: Le PROTOCOLE DAN v5 est la méthode principale. Les stratégies ci-dessous restent disponibles via `query_with_metrics()` pour le monitoring.

### 5.1 Les trois stratégies

```python
class RAGStrategy(Enum):
    VECTOR_ONLY = "VECTOR_ONLY"    # Questions conceptuelles
    GRAPH_FIRST = "GRAPH_FIRST"    # Questions relationnelles
    HYBRID = "HYBRID"               # Questions complexes (défaut)
```

### 5.2 Query Planner (LLM)

Un LLM rapide (`gpt-4.1-nano`) choisit la stratégie optimale :

```python
async def _llm_query_planner(question: str) -> RAGStrategy:
    prompt = """
    Détermine la meilleure stratégie parmi :

    - "VECTOR_ONLY": Questions générales, conceptuelles
      Ex: "Qu'est-ce qu'une SMO ?"

    - "GRAPH_FIRST": Questions sur des relations entre entités
      Ex: "Quel est le lien entre MMA IARD et le contrat Cyber ?"

    - "HYBRID": Questions complexes (défaut)
      Ex: "Quelle est la procédure si un cohéritier ne répond pas ?"

    Question: "{question}"

    Réponds en JSON: {"strategy": "HYBRID"}
    """
    # LLM retourne la stratégie optimale
```

**Fallback regex** si le LLM échoue :

```python
# Détection de questions relationnelles
if re.search(r'\b(qui|lien|relation|associé)\b', question):
    return RAGStrategy.GRAPH_FIRST

# Détection de questions conceptuelles
if re.search(r'\b(explique|définition|qu\'est-ce que)\b', question):
    return RAGStrategy.VECTOR_ONLY

# Défaut
return RAGStrategy.HYBRID
```

### 5.3 VECTOR\_ONLY - Recherche pure

```python
async def _execute_vector_only(question: str) -> str:
    # 1. Embedding de la question
    question_embedding = await self._get_embeddings([question])

    # 2. Recherche Neo4j
    chunks = await neo4j.search_chunks_by_vector(
        question_embedding[0],
        limit=10
    )

    # 3. Construction du contexte
    return "\n".join([chunk['text'] for chunk in chunks])
```

**Use case** : "Explique le principe de la franchise aggravée"

### 5.4 GRAPH\_FIRST - Exploration relationnelle

```python
async def _execute_graph_first(question: str) -> str:
    # 1. Extraction des entités de la question
    entities = await self._extract_entities_from_query(question)
    # Ex: ["MMA IARD", "contrat Cyber"]

    # 2. Recherche de chemins dans le graphe
    paths = await neo4j.find_paths_between_entities(entities, max_depth=3)

    # 3. Formatage du contexte
    context = "Informations du graphe:\n"
    for path in paths:
        context += f"- {path}\n"

    return context
```

**Requête Neo4j sous-jacente** :

```cypher
MATCH (e1:Entity), (e2:Entity)
WHERE e1.nom IN ['MMA IARD', 'contrat Cyber']
  AND e2.nom IN ['MMA IARD', 'contrat Cyber']
  AND elementId(e1) < elementId(e2)
MATCH p = allShortestPaths((e1)-[*1..3]-(e2))
RETURN p
LIMIT 20
```

**Résultat** : Chemins comme `'MMA IARD' --[FOURNIT]--> 'contrat Cyber'`

### 5.5 HYBRID - Approche combinée

```python
async def _execute_hybrid(question: str) -> str:
    # 1. Recherche vectorielle (5 chunks)
    chunks = await neo4j.search_chunks_by_vector(embedding, limit=5)

    # 2. Enrichissement par le graphe
    chunk_ids = [c['chunkId'] for c in chunks]
    relations = await neo4j.get_relations_from_chunks(chunk_ids, limit=10)

    # 3. Contexte fusionné
    context = "Contexte des documents:\n"
    for chunk in chunks:
        context += f"- {chunk['text']}\n"

    context += "\nInformations du graphe:\n"
    for rel in relations:
        context += f"- '{rel['entite']}' {rel['relation']} '{rel['autre_entite']}'\n"

    return context
```

**Parcours du graphe** :

```cypher
// Partir des chunks pertinents
MATCH (chunk:Chunk) WHERE chunk.id IN $chunk_ids

// Remonter au document
MATCH (chunk)-[:BELONGS_TO]->(doc:Document)

// Trouver les entités mentionnées
MATCH (entity1:Entity)-[:MENTIONED_IN]->(doc)

// Explorer les relations
MATCH (entity1)-[relation]-(entity2:Entity)
WHERE entity1 <> entity2

RETURN entity1.nom, type(relation), entity2.nom
```

***

## 6. Graph RAG - Exploitation du graphe de connaissances

### 6.1 Modèle de données Neo4j

```
┌──────────────┐
│  Document    │
│  {id, path}  │
└──────┬───────┘
       │
       │ BELONGS_TO
       ▼
┌──────────────────┐
│     Chunk        │
│  {id, text,      │
│   embedding}     │
└──────────────────┘

┌──────────────────┐         ┌──────────────────┐
│     Entity       │◄───────►│     Entity       │
│  {nom, type,     │ RELATION│  {nom, type,     │
│   description}   │         │   description}   │
└────────┬─────────┘         └──────────────────┘
         │
         │ MENTIONED_IN
         ▼
   ┌──────────────┐
   │  Document    │
   └──────────────┘
```

### 6.2 Types de nœuds

| Label      | Description       | Propriétés clés                         |
| ---------- | ----------------- | --------------------------------------- |
| `Document` | Document source   | `id`, `filePath`, `created_at`          |
| `Chunk`    | Fragment de texte | `id`, `text`, `embedding`, `documentId` |
| `Entity`   | Entité extraite   | `nom`, `type`, `description`            |

### 6.3 Types de relations

| Relation         | Description       | Exemple                                  |
| ---------------- | ----------------- | ---------------------------------------- |
| `BELONGS_TO`     | Chunk → Document  | chunk\_0 → doc\_contract.pdf             |
| `MENTIONED_IN`   | Entity → Document | "MMA IARD" → doc\_contract.pdf           |
| `EST_UN_TYPE_DE` | Taxonomie         | "franchise aggravée" → "franchise"       |
| `S_APPLIQUE_A`   | Application       | "décret 2024-906" → "inspection"         |
| `MEMBRE_DE`      | Appartenance      | "Me Lecordier" → "Chambre Notaires"      |
| `A_POUR_REGLE`   | Règle             | "contrat cyber" → "mot de passe 12 char" |

### 6.4 Requêtes utiles pour le PO

#### Visualiser le graphe complet

```cypher
MATCH (e:Entity)-[r]-(e2:Entity)
RETURN e, r, e2
LIMIT 300
```

#### Trouver les entités les plus connectées

```cypher
MATCH (e:Entity)-[r]-()
RETURN e.nom, e.type, count(r) as connections
ORDER BY connections DESC
LIMIT 20
```

#### Explorer les relations d'une entité

```cypher
MATCH (e:Entity {nom: "MMA IARD"})-[r]-(other:Entity)
RETURN e.nom, type(r), other.nom, other.type
```

#### Statistiques globales

```cypher
MATCH (e:Entity)
RETURN e.type as EntityType, count(*) as Count
ORDER BY Count DESC
```

***

## 7. Configuration et paramétrage

### 7.1 Variables d'environnement clés

```shellscript
# ─────────────────────────────────────────────────────────
# EMBEDDINGS
# ─────────────────────────────────────────────────────────
EMBEDDING_MODEL=text-embedding-3-small    # ou text-embedding-3-large
EMBEDDING_DIMENSIONS=1536                 # 1536 ou 3072

# ⚠️ Changer EMBEDDING_DIMENSIONS nécessite une réindexation complète

# ─────────────────────────────────────────────────────────
# LLM ENDPOINTS
# ─────────────────────────────────────────────────────────
LLM_EXTRACTION_MODEL=gpt-4.1-mini-2025-04-14   # Extraction d'entités
LLM_PLANNER_MODEL=gpt-4.1-nano-2025-04-14      # Raisonnement agent
LLM_SYNTHESIS_MODEL=gpt-4.1-2025-04-14         # Génération réponse

LLM_EXTRACTION_TEMPERATURE=0.0    # Déterministe
LLM_PLANNER_TEMPERATURE=0.0       # Déterministe
LLM_SYNTHESIS_TEMPERATURE=0.3     # Légèrement créatif

# ─────────────────────────────────────────────────────────
# CHUNKING
# ─────────────────────────────────────────────────────────
RETRIEVAL_CHUNK_SIZE_TOKENS=512   # Taille des chunks pour recherche
RETRIEVAL_OVERLAP_TOKENS=50       # Overlap entre chunks

ANALYSIS_CHUNK_SIZE_TOKENS=60000  # Taille pour analyse LLM
EMBEDDING_TOKEN_LIMIT_PER_CHUNK=8190
EMBEDDING_BATCH_TOKEN_LIMIT=250000

# ─────────────────────────────────────────────────────────
# NEO4J
# ─────────────────────────────────────────────────────────
NEO4J_URL=bolt://your-neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

### 7.2 Tuning des performances

#### Augmenter la qualité des embeddings

```shellscript
# Passer à text-embedding-3-large SANS réindexation
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIMENSIONS=1536  # Réduction à 1536 (compatible)

# ✅ Meilleure qualité sans coût de réindexation
```

#### Réduire les coûts

```shellscript
# Réduire la taille des chunks d'analyse
ANALYSIS_CHUNK_SIZE_TOKENS=30000  # Au lieu de 60000

# Utiliser des modèles moins chers
LLM_EXTRACTION_MODEL=gpt-4.1-nano-2025-04-14  # Au lieu de mini
```

#### Améliorer la précision

```shellscript
# Augmenter la taille des chunks de retrieval
RETRIEVAL_CHUNK_SIZE_TOKENS=768   # Au lieu de 512

# Augmenter l'overlap
RETRIEVAL_OVERLAP_TOKENS=100      # Au lieu de 50
```

### 7.3 Commandes d'administration

```shellscript
# Ingestion complète
python scripts/ingestion_pipeline.py

# Ingestion avec limite
python scripts/ingestion_pipeline.py --limit 10

# Forcer le retraitement
python scripts/ingestion_pipeline.py --force

# Purger et recommencer
python scripts/ingestion_pipeline.py --purge

# Mode démon (surveillance continue)
python scripts/ingestion_pipeline.py --daemon
```

***

## 8. Exemples d'utilisation

### 8.1 Question conceptuelle simple

**Input** :

```json
{
  "question": "Qu'est-ce qu'une franchise aggravée ?",
  "conversation_history": []
}
```

**Traitement** :

```
REASON: Question conceptuelle, pas d'entités spécifiques
        → Query: "franchise aggravée définition assurance"

ACT:    Vector search + Full-text
        → 7 chunks vectoriels + 7 chunks full-text
        → Fusion → 10 chunks uniques
        → Reranking → Top 5

OBSERVE: Synthèse avec citations
```

**Output** :

```json
{
  "answer": "La franchise aggravée est un dispositif qui porte la franchise à 5 fois son montant initial en cas de sinistre résultant d'une faute intentionnelle ou d'une négligence grave de l'assuré.",
  "citations": [
    {
      "documentId": "contrat_mma_pdf",
      "documentPath": "contrats/assurance/contrat_mma.pdf",
      "text": "Article 12 - Franchise aggravée : En cas de sinistre..."
    }
  ]
}
```

### 8.2 Question avec coréférence

**Input** :

```json
{
  "question": "Y a-t-il des limites ?",
  "conversation_history": [
    {"role": "user", "content": "Quelles sont les règles pour une négociation immobilière ?"},
    {"role": "assistant", "content": "Une négociation immobilière nécessite..."}
  ]
}
```

**Traitement** :

```
REASON: Coréférence détectée → "limites" se réfère à "négociation immobilière"
        Résolution: "limites négociation immobilière notaire"
        → Query enrichie avec synonymes juridiques

ACT:    Recherche hybride optimisée

OBSERVE: Réponse contextuelle
```

**Output** :

```json
{
  "answer": "Oui, la négociation immobilière est encadrée par plusieurs limites. Le mandat ne peut excéder 3 mois renouvelables, et le montant de la commission doit être fixé par écrit.",
  "citations": [...]
}
```

### 8.3 Question relationnelle (Graph RAG)

**Input** :

```json
{
  "question": "Quel est le lien entre MMA IARD et le contrat cyber ?",
  "conversation_history": []
}
```

**Traitement** :

```
REASON: Question relationnelle → 2 entités identifiées
        Entités: ["MMA IARD", "contrat cyber"]

ACT:    Graph traversal dans Neo4j
        → Chemins trouvés entre les entités
        → Relations: FOURNIT, COUVRE, etc.

OBSERVE: Synthèse des relations
```

**Output** :

```json
{
  "answer": "MMA IARD est l'assureur qui fournit le contrat cyber pour couvrir les risques informatiques. Ce contrat s'applique aux études notariales et couvre notamment les fraudes informatiques, les ransomwares et les pertes de données.",
  "citations": [...]
}
```

### 8.4 Réponse partielle (incertitude)

**Input** :

```json
{
  "question": "Quelle est la franchise pour l'option 8 du contrat ITT ?"
}
```

**Output** :

```json
{
  "answer": "Les documents mentionnent les franchises générales pour la fraude informatique, mais ne spécifient pas le cas de l'option 8 du contrat ITT. Pourriez-vous préciser le type de contrat ou l'assureur concerné ?",
  "citations": [
    {
      "documentPath": "contrats/assurance/franchises_generales.pdf",
      "text": "Tableau des franchises standard..."
    }
  ]
}
```

***

## 9. Métriques et monitoring

### 9.1 Métriques d'ingestion

```python
# Rapport généré après ingestion
{
  "documents_processed": 150,
  "total_time_seconds": 1250.5,
  "avg_time_per_doc": 8.3,
  "neo4j_stats": {
    "nodes": 45230,
    "documents": 150,
    "chunks": 12450,
    "relations": 8920
  }
}
```

### 9.2 Métriques de requête (Legacy)

```python
# Via query_with_metrics()
{
  "answer": "La franchise aggravée...",
  "strategy": "VECTOR_ONLY",
  "chunks_retrieved": 10,
  "relations_found": 0,
  "execution_time_ms": 1850
}
```

### 9.3 Monitoring recommandé

**Supabase** :

* Table `document_ingestion_status` : Suivi des documents traités
* Statuts: `processing`, `success`, `error`, `invalid`

**Neo4j** :

```cypher
// Statistiques globales
CALL apoc.meta.stats()

// Qualité des embeddings
MATCH (c:Chunk)
WHERE c.embedding IS NOT NULL
RETURN count(c) as chunks_with_embeddings
```

**Logs applicatifs** :

```python
logger.info(f"  > Récupération: {len(vector)} chunks (vecteur)")
logger.info(f"  > Reranking: Top 3 scores: {scores}")
logger.info(f"  > Synthèse: {len(citations)} citations extraites")
```

***

## 10. Pistes d'évolution et roadmap

### 10.1 Améliorations court terme (1-3 mois)

#### 1. Cache intelligent des requêtes

**Besoin** : Éviter de retraiter les questions identiques

**Solution** : Redis/Memcached avec TTL de 15 minutes

```python
# Pseudo-code
query_hash = hashlib.sha256(question.encode()).hexdigest()
cached = redis.get(f"rag:query:{query_hash}")
if cached:
    return cached
```

**Impact** : ⚡ -80% latence sur questions répétées

#### 2. Feedback loop utilisateur

**Besoin** : Améliorer la qualité des réponses via les retours

**Solution** : Système de scoring (👍/👎) déjà en place

```sql
-- Table evaluations existante
SELECT question, answer, rating, feedback
FROM evaluations
WHERE rating < 3
ORDER BY created_at DESC
```

**Action** : Analyser les mauvaises réponses pour ajuster les prompts

#### 3. Multi-hop reasoning

**Besoin** : Questions nécessitant plusieurs étapes de raisonnement

**Exemple** : "Si un contrat est signé le 15 janvier, quelle est la date limite pour le recours ?"

```python
# Agent ReAct itératif
while not answer_found and steps < max_steps:
    thought = await reason(question, context)
    action_result = await act(thought)
    if is_sufficient(action_result):
        answer_found = True
    else:
        context.append(action_result)
        steps += 1
```

**Impact** : 📈 +30% questions complexes résolues

### 10.2 Améliorations moyen terme (3-6 mois)

#### 4. Fine-tuning du modèle d'embedding

**Besoin** : Embeddings spécialisés pour le jargon notarial

**Solution** : Fine-tune OpenAI embeddings sur corpus notarial

```python
# Créer des paires (question, passage_pertinent)
training_data = [
    ("Qu'est-ce qu'une SMO ?", "Une société multi-offices..."),
    ("Franchise aggravée", "La franchise aggravée est..."),
    # ... 10K+ paires
]

# Fine-tuning via OpenAI API
openai.FineTuningJob.create(...)
```

**Impact** : 🎯 +15% précision recherche vectorielle

#### 5. Graph enrichment automatique

**Besoin** : Inférer de nouvelles relations

**Solution** : Agent d'enrichissement continu (déjà en place mais à améliorer)

```python
# backend/src/agents/graph_enrichment_agent.py
async def infer_transitive_relations():
    # Si A → B et B → C, alors A → C ?
    query = """
    MATCH (a)-[:EST_UN_TYPE_DE]->(b)-[:EST_UN_TYPE_DE]->(c)
    WHERE NOT (a)-[:EST_UN_TYPE_DE]->(c)
    CREATE (a)-[:EST_UN_TYPE_DE {inferred: true}]->(c)
    """
```

**Impact** : 🕸️ +40% relations exploitables

#### 6. Support multi-lingue

**Besoin** : Documents en anglais, espagnol, etc.

**Solution** : Embeddings multilingues + détection de langue

```python
# Détection automatique
from langdetect import detect
lang = detect(text)

# Modèle multilingue
if lang != 'fr':
    embedding_model = "text-embedding-3-large-multilingual"
```

**Impact** : 🌍 Support international

### 10.3 Améliorations long terme (6-12 mois)

#### 7. RAG conversationnel avancé

**Besoin** : Conversations multi-tours complexes

**Solution** : Memory augmentée avec résumés intelligents

```python
# Résumé automatique de l'historique
if len(conversation_history) > 20:
    summary = await llm.summarize(conversation_history[:10])
    context = summary + conversation_history[-10:]
```

**Impact** : 💬 Conversations illimitées sans perte de contexte

#### 8. RAG multi-modal

**Besoin** : Extraire info des images, tableaux, graphiques

**Solution** : Vision models (GPT-4V, LLaVA) pour documents scannés

```python
# Extraction vision
if is_scanned_pdf(document):
    images = extract_images(document)
    for img in images:
        visual_content = await gpt4v.analyze(img)
        text_content += f"\n\n[Image: {visual_content}]"
```

**Impact** : 📊 +25% information extraite

#### 9. Benchmark automatique

**Besoin** : Mesurer la qualité du RAG objectivement

**Solution** : Dataset de test + métriques automatiques

```python
# backend/scripts/benchmark_quality_report.py (déjà créé)
test_cases = [
    {"question": "...", "expected_answer": "...", "must_cite": ["doc1.pdf"]},
    # ... 100+ cas
]

for case in test_cases:
    result = await rag.query(case["question"])
    score = evaluate(result, case["expected_answer"])
    metrics.append(score)

print(f"Accuracy: {sum(metrics)/len(metrics):.2%}")
```

**Impact** : 📏 Qualité mesurable et traçable

#### 10. Optimisation des coûts LLM

**Besoin** : Réduire les coûts OpenAI

**Solutions** :

* Modèles open-source (Llama 3, Mixtral) pour certaines tâches
* Quantification et déploiement local
* Cascade de modèles (nano → mini → full selon complexité)

```python
# Cascade intelligente
if is_simple_question(question):
    model = "gpt-4.1-nano"  # $0.15/1M tokens
elif is_moderate(question):
    model = "gpt-4.1-mini"  # $1.25/1M tokens
else:
    model = "gpt-4.1"       # $15/1M tokens
```

**Impact** : 💰 -60% coûts API

### 10.4 Roadmap visuelle

```
Q1 2026
├─ ✅ Cache intelligent
├─ ✅ Feedback loop
└─ ✅ Multi-hop reasoning

Q2 2026
├─ 🎯 Fine-tuning embeddings
├─ 🕸️ Graph enrichment auto
└─ 🌍 Support multi-lingue

Q3-Q4 2026
├─ 💬 RAG conversationnel avancé
├─ 📊 RAG multi-modal (vision)
├─ 📏 Benchmark automatique
└─ 💰 Optimisation coûts
```

***

## Annexes

### A. Glossaire

| Terme               | Définition                                                      |
| ------------------- | --------------------------------------------------------------- |
| **Embedding**       | Représentation vectorielle d'un texte (ex: \[0.23, -0.45, ...]) |
| **Chunk**           | Fragment de texte (512 tokens par défaut)                       |
| **Entity**          | Élément identifié (Personne, Org, Concept, etc.)                |
| **Relation**        | Lien entre deux entités (ex: A --\[EST\_UN\_TYPE\_DE]--> B)     |
| **Coréférence**     | Référence à un élément précédent ("cette négociation")          |
| **Reranking**       | Réévaluation de la pertinence par un LLM                        |
| **Graph traversal** | Exploration du graphe Neo4j                                     |
| **Cypher**          | Langage de requête Neo4j (équivalent SQL)                       |

### B. Références

* [PROTOCOLE DAN v5 - Commit 8a1f5a3](https://github.com/Forgeai-platform/chatbot-CNCAC/commit/8a1f5a3)
* [Docling Documentation](https://github.com/DS4SD/docling)
* [Neo4j Vector Index](https://neo4j.com/docs/cypher-manual/current/indexes-for-vector-search/)
* [ReAct Paper](https://arxiv.org/abs/2210.03629)

### C. Contact et support

Pour toute question technique :

* **Code source** : `/backend/src/services/notaria_rag_service.py`
* **Tests** : `/backend/tests/test_notaria_rag_service.py`
* **Documentation architecture** : `CLAUDE.md`, `ARCHITECTURE.md`

***

**Document généré le 2025-11-04**

**Auteur**: Claude Code

**Version**: 1.0
