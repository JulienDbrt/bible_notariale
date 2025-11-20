# UI de Recherche & Knowledge Base

# &#x20;**3 objectifs stratégiques** :

1. **🐛 Debug technique** : Vérifier ce que le RAG trouve vraiment
2. **📚 Base de connaissance** : Accès direct pour les notaires (sans chatbot)
3. **✅ Quality assurance** : Valider la cohérence avant même les tests

***

## 🎯 **FONCTIONNALITÉS PROPOSÉES**

### **Page 1 : Recherche Avancée de Documents**



typescript

````
// Interface de recherche avec filtresinterfaceSearchFilters{ query:string;// Recherche full-text collections?:string[];// ["DEONTOLOGIE", "IMMOBILIER", ...] dateRange?:[Date,Date];// Filtrer par date de publication documentTypes?:string[];// ["RPN", "Contrat", "Guide", ...] priorityMin?:number;// Niveau de priorité (1-10) onlyWithEntities?:boolean;// Docs avec entités extraites}interfaceSearchResult{ documentId:string; title:string; collection:string; excerpt:string;// Extrait avec termes surlignés matchScore:number;// Score de pertinence entities:Entity[];// Entités liées chunkCount:number;// Nombre de chunks lastIndexed:Date;}```**Wireframe concept :** ```┌─────────────────────────────────────────────────────────────┐ │ 🔍 KnowledgeBaseSearch[UserMenu] │ ├─────────────────────────────────────────────────────────────┤ │ │ │ [Search query...][🔍 Search] │ │ │ │ Filters:[🏷️ Collections ▼][📅 Date ▼][⚡ Priority ▼] │ │ │ ├─────────────────────────────────────────────────────────────┤ │ Results:47 documents found Sort by:[▼] │ ├─────────────────────────────────────────────────────────────┤ │ ┌─────────────────────────────────────────────────────────┐│ │ │ 📄 RPN-Règlement ProfessionnelNational ⭐⭐⭐⭐⭐ ││ │ │ DEONTOLOGIE • Réglementaire • Mis à jour:2024-01-15 ││ │ │ ...concernant le secret professionnel et les conflits ││ │ │ d'intérêt dans l'exercice de la fonction notariale... ││ │ │ [👁️ View][🔗 Entities:45][📊 Chunks:120] ││ │ └─────────────────────────────────────────────────────────┘│ │ ┌─────────────────────────────────────────────────────────┐│ │ │ 📄 ContratCyberMMAIARD ⭐⭐⭐⭐ ││ │ │ ASSURANCES • Contrat • Échéance:2025-12-31 ││ │ └─────────────────────────────────────────────────────────┘│ └─────────────────────────────────────────────────────────────┘
````

***

### **Page 2 : Visualisation d'un Document**



typescript

````
interfaceDocumentView{ metadata:{ title:string; collection:string; source:string; uploadDate:Date; fileSize:number; status:"indexed"|"processing"|"error";}; chunks:{ id:string; text:string; position:number; entities:Entity[]; embedding_quality?:number;// Score de qualité de l'embedding}[]; statistics:{ totalChunks:number; uniqueEntities:number; avgChunkLength:number; indexationTime:number;}; qualityChecks:{ hasOrphanChunks:boolean;// Chunks sans entités hasDuplicates:boolean;// Chunks en doublon lowQualityChunks:number;// Chunks avec peu de contenu};}```**Wireframe :** ```┌─────────────────────────────────────────────────────────────┐ │ ← Back to Search 📄 RPN-Règlement Professionnel │ ├─────────────────────────────────────────────────────────────┤ │ 📊 Statistics │ │ • 120 chunks indexed │ │ • 45 entities extracted │ │ • Collection:DEONTOLOGIE │ │ • Priority:⭐⭐⭐⭐⭐(10/10) │ │ • Last update:2024-01-15 │ │ │ │ ⚠️ QualityIssues: │ │ • 3 chunks with no entities │ │ • 1 potential duplicate │ │ │ │ [🔍 ViewChunks][🕸️ ViewGraph][⚙️ Re-index] │ ├─────────────────────────────────────────────────────────────┤ │ ChunksPreview(120 total)[Filter by: ▼] │ │ │ │ ┌─────────────────────────────────────────────────────────┐│ │ │ Chunk #1(512 tokens)Quality: ✓ Good│││ │ L'article 29.1 du RPN définit l'attribution des ││ │ │ minutes comme le droit accordé au notaire... ││ │ │ ││ │ │ 🏷️ Entities:[RPN][Article29][Attribution minutes] ││ │ │ [📝 Edit][🗑️ Delete][⚡ ViewinGraph] ││ │ └─────────────────────────────────────────────────────────┘│ └─────────────────────────────────────────────────────────────┘
````

***

### **Page 3 : Explorateur de Graph (Interactive)**

Visualisation Neo4j style avec D3.js ou vis.js :



typescript

````
interfaceGraphExplorer{ centerNode:Entity;// Entité centrale depth:number;// Profondeur d'exploration (1-3) filters:{ minPriority:number; nodeTypes:string[];// ["Institution", "Regulation", ...] relationTypes:string[];// ["CONTIENT", "CITE", ...]};}// Interactions :// - Click sur un nœud : affiche détails + chunks liés// - Double-click : recenter le graph sur ce nœud// - Drag : réorganiser la vue// - Hover : preview rapide```**Wireframe :** ```┌─────────────────────────────────────────────────────────────┐ │ 🕸️ KnowledgeGraphExplorer[🎛️ Filters] │ ├─────────────────────────────────────────────────────────────┤ │ Search entity:[RPN][🔍] │ │ Depth:[●──────]2 hops Priority:[●────] ≥8 │ ├─────────────────────────────────────────────────────────────┤ │ │ │ ⚪ Article29 │ │ │ │ │ │ CONTIENT │ │ ▼ │ │ ┌─────────┐ CITE ┌──────────────┐ │ │ │ RPN │────────────────▶│ SecretProf.│ │ │ └─────────┘ └──────────────┘ │ │ │ │ │ │ PUBLIE_PAR │ │ ▼ │ │ ⚪ CSN │ │ │ ├─────────────────────────────────────────────────────────────┤ │ Selected:RPN │ │ • Type:Regulation │ │ • Priority:10 │ │ • Connected to:45 entities │ │ • Referencedin:120 chunks │ │ [📄 ViewDocuments][🔗 ExportGraph] │ └─────────────────────────────────────────────────────────────┘
````

***

### **Page 4 : Comparateur de Recherches (Debug RAG)**

Permet de comparer ce que trouve le RAG vs recherche manuelle :



typescript

````
interfaceRAGComparison{ query:string; ragResults:{ strategy:"ReAct"|"Vector"|"Hybrid"; reasoningStep:string;// Pensée du LLM selectedDocuments:Document[]; retrievedChunks:Chunk[]; executionTime:number;}; manualSearch:{ userSelectedDocs:Document[]; expectedChunks:Chunk[];}; diff:{ missedRelevantDocs:Document[];// Docs manqués par le RAG irrelevantRetrieved:Document[];// Docs non pertinents récupérés precision:number; recall:number;};}```**Wireframe :** ```┌─────────────────────────────────────────────────────────────┐ │ 🔬 RAGDebugComparator │ ├─────────────────────────────────────────────────────────────┤ │ TestQuestion: │ │ [Collaboratrice achète bien, vendeurs peuvent passer par ce │ │ notaire ?][Test] │ ├─────────────────────────────────────────────────────────────┤ │ ┌────────────────────────┬────────────────────────────────┐│ │ │ 🤖 RAGResults │ 👤 ExpectedResults ││ │ ├────────────────────────┼────────────────────────────────┤│ │ │ Strategy:ReAct │ Manual selection: ││ │ │ Reasoning: │ ✓ RPN(Art.29) ││ │ │ "Question about │ ✓ Règlement CourCaen ││ │ │ déontologie..." │ ✗ Guide négo immo(excluded) ││ │ │ │ ││ │ │ Documents found: │ Missing: ││ │ │ ❌ Guide négo immo │ • RPN(Art.29) ⚠️ ││ │ │ ✓ RPN │ • Règlement Cour ⚠️ ││ │ │ │ ││ │ │ Precision:50% │ Irrelevant retrieved: ││ │ │ Recall:50% │ • Guide négo immo ││ │ │ Time:2.3s │ ││ │ └────────────────────────┴────────────────────────────────┘│ │ │ │ 📊 Analysis: │ │ • Collection mismatch:UsedIMMOBILIER instead ofDEONTO │ │ • Suggestion:Add collection routing(see Optim #1) │ └─────────────────────────────────────────────────────────────┘
````

***

### **Page 5 : Quality Dashboard**

Vue d'ensemble de la santé du knowledge base :



typescript

````
interfaceQualityDashboard{ overview:{ totalDocuments:number; totalChunks:number; totalEntities:number; lastIndexation:Date;}; healthMetrics:{ orphanChunks:number;// Chunks sans entités lowQualityEmbeddings:number;// Embeddings suspects duplicateChunks:number; missingMetadata:number;}; collectionStats:{ collection:string; docCount:number; coverage:number;// % de thématiques couvertes avgPriority:number;}[]; recentIssues:{ type:"missing_source"|"duplicate"|"low_quality"; documentId:string; severity:"low"|"medium"|"high"; suggestion:string;}[];}```**Wireframe :** ```┌─────────────────────────────────────────────────────────────┐ │ 📊 KnowledgeBaseHealthDashboard │ ├─────────────────────────────────────────────────────────────┤ │ OverviewLast sync: 1h │ │ ┌───────────┬───────────┬───────────┬───────────┐ │ │ │ 234 │ 2,847 │ 456 │ 94.2% │ │ │ │ Documents │ Chunks │ Entities │ Health │ │ │ └───────────┴───────────┴───────────┴───────────┘ │ │ │ │ ⚠️ IssuesDetected(12) │ │ ┌─────────────────────────────────────────────────────────┐│ │ │ 🔴 High:8 chunks without entities ││ │ │ → Documents:RPN,ContratCyber,Guide négo ││ │ │ [🔍 Inspect][⚡ Re-index] ││ │ │ ││ │ │ 🟡 Medium:23 duplicate chunks detected ││ │ │ → Likelyfrom version updates ││ │ │ [🗑️ Clean up][📋 Review] ││ │ │ ││ │ │ 🟢 Low:3 documents missing collection tag ││ │ │ [🏷️ Tag now] ││ │ └─────────────────────────────────────────────────────────┘│ │ │ │ CollectionCoverage[View details] │ │ DEONTOLOGIE ████████████████░░ 85%(45 docs) │ │ IMMOBILIER ███████████░░░░░░░ 65%(28 docs) │ │ ASSURANCES ███████████████████ 95%(12 docs) │ │ RH ████████░░░░░░░░░░ 50%(8 docs) │ │ PROCEDURE ████████████░░░░░░ 70%(15 docs) │ └─────────────────────────────────────────────────────────────┘
````

***

## 🛠️ **IMPLÉMENTATION TECHNIQUE**

### **Stack proposée (cohérente avec l'existant)**



typescript

```
// Frontend: Next.js 15 + TypeScriptfrontend/├── app/│ ├── knowledge-base/│ │ ├── page.tsx// Page 1: Search│ │ ├── document/[id]/page.tsx// Page 2: Document view│ │ ├── graph/page.tsx// Page 3: Graph explorer│ │ ├── compare/page.tsx// Page 4: RAG comparator│ │ └── dashboard/page.tsx// Page 5: Quality dashboard│ └── ...├── components/│ ├── knowledge-base/│ │ ├── SearchFilters.tsx│ │ ├── DocumentCard.tsx│ │ ├── ChunkViewer.tsx│ │ ├── GraphVisualization.tsx// Using vis.js│ │ └── QualityMetrics.tsx│ └── ...└── lib/ └── api/ └── knowledge-base.ts// API client// Backend: FastAPIbackend/├── src/│ ├── api/│ │ └── knowledge_base.py// Nouveaux endpoints│ ├── services/│ │ ├── knowledge_search_service.py// Service de recherche│ │ └── graph_explorer_service.py// Service d'exploration│ └── ...
```

***

### **Nouveaux Endpoints API**



python

```
# backend/src/api/knowledge_base.pyfrom fastapi import APIRouter, Query from typing import List, Optional from pydantic import BaseModel router = APIRouter(prefix="/api/knowledge-base", tags=["Knowledge Base"])# 1. Recherche avancée@router.post("/search")asyncdefsearch_documents( query:str, collections: Optional[List[str]]=None, date_range: Optional[tuple]=None, priority_min: Optional[int]=None, limit:int=20)-> SearchResults:"""Recherche avancée dans les documents."""pass# 2. Détails d'un document@router.get("/documents/{document_id}")asyncdefget_document_details(document_id:str)-> DocumentView:"""Récupère tous les détails d'un document avec ses chunks."""pass# 3. Exploration du graph@router.get("/graph/explore")asyncdefexplore_graph( entity:str, depth:int=2, min_priority:int=5)-> GraphData:"""Explore le knowledge graph autour d'une entité."""pass# 4. Comparaison RAG vs Manuel@router.post("/compare")asyncdefcompare_rag_results( query:str, expected_docs: List[str])-> RAGComparison:"""Compare résultats RAG vs sélection manuelle."""# Exécuter le RAG rag_results =await rag_service.query_with_react(query)# Calculer precision/recall retrieved_ids =[doc.idfor doc in rag_results.documents] precision =len(set(retrieved_ids)&set(expected_docs))/len(retrieved_ids) recall =len(set(retrieved_ids)&set(expected_docs))/len(expected_docs)return{"rag_results": rag_results,"expected_docs": expected_docs,"precision": precision,"recall": recall,"missed":list(set(expected_docs)-set(retrieved_ids)),"irrelevant":list(set(retrieved_ids)-set(expected_docs))}# 5. Dashboard qualité@router.get("/quality/dashboard")asyncdefget_quality_dashboard()-> QualityDashboard:"""Vue d'ensemble de la santé du knowledge base."""return{"overview":await get_overview_stats(),"health_metrics":await check_health_issues(),"collection_stats":await get_collection_coverage(),"recent_issues":await get_recent_issues()}# 6. Actions de curation@router.post("/documents/{document_id}/re-index")asyncdefreindex_document(document_id:str):"""Ré-indexe un document spécifique."""pass@router.delete("/chunks/{chunk_id}")asyncdefdelete_chunk(chunk_id:str):"""Supprime un chunk de mauvaise qualité."""pass@router.patch("/entities/{entity_id}")asyncdefupdate_entity(entity_id:str, updates:dict):"""Met à jour les métadonnées d'une entité."""pass
```

***

### **Service de recherche (Neo4j)**



python

```
# backend/src/services/knowledge_search_service.pyclassKnowledgeSearchService:def__init__(self, neo4j_service: Neo4jService): self.neo4j = neo4j_service asyncdefadvanced_search( self, query:str, collections: List[str]=None, priority_min:int=None)-> List[SearchResult]:"""  Recherche avancée avec filtres multiples.  Combine full-text search + vector search + filtres.  """# 1. Full-text search sur les chunks cypher ="""  CALL db.index.fulltext.queryNodes('chunkTextIndex', $query)  YIELD node AS chunk, score  // Remonter au document  MATCH (chunk)-[:PART_OF]->(doc:Document)  // Filtres optionnels  WHERE ($collections IS NULL OR doc.collection IN $collections)  AND ($priority_min IS NULL OR doc.priority >= $priority_min)  // Agréger par document  WITH doc,  MAX(score) as maxScore,  COLLECT(chunk.text)[0..3] as excerpts  // Récupérer les entités liées  OPTIONAL MATCH (doc)<-[:PART_OF]-(c)-[:HAS_ENTITY]->(e:Entity)  WITH doc, maxScore, excerpts, COLLECT(DISTINCT e) as entities  RETURN doc, maxScore, excerpts, entities  ORDER BY maxScore DESC  LIMIT 50  """ results =await self.neo4j.run_query(cypher,{"query": query,"collections": collections,"priority_min": priority_min })return[self._format_search_result(r)for r in results]asyncdefget_document_health(self, document_id:str)->dict:"""Analyse la santé d'un document spécifique.""" cypher ="""  MATCH (doc:Document {documentId: $doc_id})  OPTIONAL MATCH (doc)<-[:PART_OF]-(chunk:Chunk)  OPTIONAL MATCH (chunk)-[:HAS_ENTITY]->(entity:Entity)  WITH doc,  COUNT(DISTINCT chunk) as total_chunks,  COUNT(DISTINCT entity) as total_entities,  COUNT(DISTINCT CASE WHEN entity IS NULL THEN chunk END) as orphan_chunks  RETURN doc, total_chunks, total_entities, orphan_chunks  """ result =await self.neo4j.run_query(cypher,{"doc_id": document_id})return{"totalChunks": result[0]["total_chunks"],"uniqueEntities": result[0]["total_entities"],"hasOrphanChunks": result[0]["orphan_chunks"]>0,"orphanChunksCount": result[0]["orphan_chunks"]}
```

***

## 📅 **PLANNING D'IMPLÉMENTATION**

### **Phase 1 : MVP (5 jours)** ⭐ **PRIORITAIRE**

**Jour 1-2 : Backend API**

* &#x20;Endpoint `/search` avec filtres basiques
* &#x20;Endpoint `/documents/{id}` avec chunks
* &#x20;Endpoint `/quality/dashboard` avec métriques

**Jour 3-4 : Frontend de base**

* &#x20;Page recherche avec filtres
* &#x20;Page détails document
* &#x20;Dashboard qualité simple

**Jour 5 : Intégration**

* &#x20;Tests end-to-end
* &#x20;Documentation utilisateur

**Livrable :** Interface utilisable pour debug et recherche basique

***

### **Phase 2 : Avancé (3 jours)** 🚀

**Jour 1 : Graph Explorer**

* &#x20;Intégration vis.js ou D3.js
* &#x20;Endpoint `/graph/explore`
* &#x20;Interface interactive

**Jour 2 : RAG Comparator**

* &#x20;Endpoint `/compare`
* &#x20;Interface side-by-side
* &#x20;Métriques precision/recall

**Jour 3 : Actions de curation**

* &#x20;Boutons re-index
* &#x20;Suppression chunks
* &#x20;Édition métadonnées

**Livrable :** Outil complet de debug et curation

***

## 🎯 **VALEUR AJOUTÉE**

### **Pour le projet actuel (Phase 1 bis) :**

1. **Debug accéléré** : Voir immédiatement pourquoi TEST\_DEON\_001 échoue 
   * "Ah ! Le système trouve 'Guide négo immo' au lieu de 'RPN'"
   * Action : Re-router vers collection DEONTOLOGIE
2. **Validation des optimisations** : Tester impact des changements 
   * Avant Optim #1 : 10 docs trouvés, 3 pertinents
   * Après Optim #1 : 5 docs trouvés, 5 pertinents ✅
3. **Création du corpus de test** : Delphine peut explorer facilement 
   * "Tiens, on a 45 docs sur la déontologie"
   * "Il manque des infos sur les successions"

### **Pour la Phase 2 (long terme) :**

1. **Base de connaissance autonome** : Les notaires peuvent chercher sans chatbot 
   * Plus rapide pour trouver un article précis
   * Pas de risque d'hallucination
2. **Curation continue** : Maintenir la qualité 
   * Identifier les trous documentaires
   * Nettoyer les doublons
   * Valider les extractions d'entités
3. **Formation des utilisateurs** : Montrer "sous le capot" 
   * Rassure sur la fiabilité
   * Explique comment améliorer les questions
