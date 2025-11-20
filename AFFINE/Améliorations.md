# Améliorations

# PLAN D'AMÉLIORATION CHATBOT - Synthèse Complète

## Chambre des Notaires de Caen - Phase 1 bis

**Version** : 1.0
**Date** : 18 novembre 2025
**Contexte** : 10/15 tests échoués, pattern clair = mauvaise sélection de sources

***

## 📈 SYNTHÈSE STRATÉGIQUE PAR IMPACT/EFFORT

| #      | Optimisation                      | Impact | Effort | Priorité      | Type              |
| ------ | --------------------------------- | ------ | ------ | ------------- | ----------------- |
| **1**  | Collections thématiques + Routing | ⭐⭐⭐⭐⭐  | 2j     | 🔥 CRITIQUE   | Sélection sources |
| **2**  | Top-k + Reranking LLM             | ⭐⭐⭐⭐⭐  | 1j     | 🔥 CRITIQUE   | Recherche         |
| **3**  | Enrichissement métadonnées Bible  | ⭐⭐⭐⭐⭐  | 0.5j   | 🔥 CRITIQUE   | Fondation         |
| **4**  | Prompt expertise notariale        | ⭐⭐⭐⭐   | 0.5j   | 🔥 HAUTE      | Qualité réponse   |
| **5**  | Détection hors périmètre          | ⭐⭐⭐⭐   | 1j     | 🔥 HAUTE      | Fiabilité         |
| **6**  | Expansion requête (lexique)       | ⭐⭐⭐⭐   | 0.5j   | ⚡ RAPIDE      | Recherche         |
| **7**  | Boost questions typiques          | ⭐⭐⭐⭐   | 1j     | ⚡ RAPIDE      | Bible             |
| **8**  | Caching embeddings                | ⭐⭐⭐    | 0.5j   | ⚡ RAPIDE      | Performance       |
| **9**  | Parallélisation recherche         | ⭐⭐⭐    | 0.5j   | ⚡ RAPIDE      | Performance       |
| **10** | Boost vocabulaire spécifique      | ⭐⭐⭐    | 0.5j   | 🟢 MOYEN      | Bible             |
| **11** | Graph traversal relations         | ⭐⭐⭐⭐   | 1.5j   | 🟢 MOYEN      | Multi-docs        |
| **12** | Graph traversal entités           | ⭐⭐⭐    | 2j     | 🟡 LONG TERME | Précision         |
| **13** | Chunking avec overlap             | ⭐⭐⭐    | 1.5j   | 🟡 LONG TERME | Re-indexation     |

**TOTAL CRITIQUE + HAUTE** : 5.5 jours → Objectif 80% atteint
**TOTAL avec RAPIDE** : 8 jours → Système optimisé
**TOTAL complet** : 12 jours → Excellence

***

## 🎯 ANALYSE DES PROBLÈMES ACTUELS

### **Problème #1 : Mauvaise sélection de sources (70% des échecs)**

**Tests échoués** :

* TEST\_DEON\_001 : Guide négo immo au lieu du RPN
* TEST\_IMMO\_001/002 : Mauvaises sources
* TEST\_RH\_001 : Mauvaises sources
* TEST\_ASSUR\_001 : Mauvaises sources

**Cause** : 234 documents interrogés uniformément, pas de filtrage intelligent

**Solutions** : #1, #3, #6

***

### **Problème #2 : Réponses incomplètes (20% des échecs)**

**Tests échoués** :

* TEST\_USER\_001 : Info partielle
* TEST\_USER\_007 : Contexte manquant

**Cause** : top\_k = 5 trop faible, pas de reranking

**Solutions** : #2, #7, #11

***

### **Problème #3 : Qualité juridique insuffisante (10% des échecs)**

**Tests échoués** :

* TEST\_DEON\_001 : Ne mentionne pas le conflit d'intérêts

**Cause** : Prompts génériques, pas calibrés métier notarial

**Solutions** : #4, #5

***

## 🔥 PRIORITÉ CRITIQUE (5.5 jours) - Objectif 80%

### **#1. Collections thématiques + Document Routing**

**Impact** : ⭐⭐⭐⭐⭐ (-70% erreurs de sources)
**Effort** : 2 jours

**Problème** : Les 234 documents sont traités uniformément. Question sur déontologie → cherche aussi dans guides immobiliers.

**Solution en 2 étapes** :

#### **Étape 1A : Enrichir Neo4j avec catégories métier**



python

```
# scripts/enrich_neo4j_categories.py# Charger métadonnées validéesmetadata_dir = Path("_metadata/documents")for meta_file in metadata_dir.glob("*.metadata.json"): metadata = json.load(open(meta_file)) query ="""  MATCH (doc:Document {documentId: $doc_id})  SET doc.categories_metier = $categories,  doc.type_document = $type,  doc.priorite = $priorite  """await neo4j.run(query,{"doc_id": metadata["document_id"],"categories": metadata.get("categories_metier",[]),"type": metadata["classification"]["type_document"],"priorite": metadata.get("priorite",5)})
```

#### **Étape 1B : Routing avant recherche**



python

```
# backend/app/services/notaria_rag_service.pyasyncdef_reasoning_step(self, question:str):"""AJOUT : Routing intelligent."""# 1. Classifier la question par catégorie categories =await self._classify_question(question)# 2. Filtrer documents par catégorie + priorité relevant_doc_ids =await self._filter_docs_by_category(categories)# 3. Recherche vectorielle UNIQUEMENT dans docs pertinents chunks =await self.neo4j.hybrid_search( query=question, document_filter=relevant_doc_ids,# NOUVEAU top_k=20)return chunks asyncdef_classify_question(self, question:str)-> List[str]:"""LLM léger pour identifier 1-2 catégories pertinentes.""" prompt =f"""  Classifie cette question notariale :  Catégories possibles :  - DEONTOLOGIE : secret professionnel, conflits, RPN, sanctions  - IMMOBILIER : négociation, mandats, transactions, vente  - RH : salaires, CCN, congés, licenciement, formation  - ASSURANCES : cyber, RCP, garanties, franchises  - PROCEDURE : médiation, réclamations, tribunal, discipline  - FISCAL : impôts, TPF, droits mutation  - SUCCESSION : héritage, testament, partage  Question: {question} Retourne JSON: ["CATEGORIE1", "CATEGORIE2"]  Maximum 2 catégories, ordonnées par pertinence.  """ response =await self.extraction_client.chat.completions.create( model="gpt-4o-mini", messages=[{"role":"user","content": prompt}], temperature=0)return json.loads(response.choices[0].message.content)asyncdef_filter_docs_by_category(self, categories: List[str])-> List[str]:"""Récupère les documents dans ces catégories, triés par priorité.""" query ="""  MATCH (doc:Document)  WHERE ANY(cat IN doc.categories_metier WHERE cat IN $categories)  RETURN doc.documentId as doc_id  ORDER BY doc.priorite DESC  LIMIT 50  """ result =await self.neo4j.run(query,{"categories": categories})return[record["doc_id"]for record in result]
```

**Résultat attendu** :

* Question déontologie → cherche dans 45 docs au lieu de 234
* Documents priorité 10 (RPN, Code) en premier
* -70% d'erreurs de sélection de sources

***

### **#2. Top-k augmenté + Reranking LLM**

**Impact** : ⭐⭐⭐⭐⭐ (+50% complétude)
**Effort** : 1 jour

**Problème** : top\_k = 5 trop faible → contexte insuffisant. Pas de reranking → chunks médiocres passent.

**Solution** :



python

```
# backend/app/services/notaria_rag_service.pyasyncdef_acting_step(self, question:str, chunks: List):"""MODIFICATION : Plus de chunks + reranking."""# 1. Phase initiale : récupérer LARGEMENT (20 chunks) initial_chunks = chunks[:20]# Au lieu de 5# 2. NOUVEAU : Reranking avec LLM best_chunks =await self._rerank_with_llm(question, initial_chunks, target=8)# 3. Synthèse (code existant) answer =await self._synthesize_answer(question, best_chunks)return answer asyncdef_rerank_with_llm( self, question:str, chunks: List, target:int=8)-> List:"""Reranke avec gpt-4o-mini pour scorer chaque chunk."""# Formater les chunks chunks_formatted ="\n\n".join([f"[Passage {i+1}]\n{chunk.text[:300]}..."for i, chunk inenumerate(chunks)]) prompt =f"""  Question: {question} Score chaque passage de 0 à 10 selon sa pertinence pour répondre.  Critères:  - 10 : Répond directement à la question  - 7-9 : Contient des éléments de réponse importants  - 4-6 : Contexte utile mais pas essentiel  - 0-3 : Peu ou pas pertinent  Passages: {chunks_formatted} Retourne UNIQUEMENT un JSON:  [{{"passage_id": 1, "score": 8}}, {{"passage_id": 2, "score": 5}}, ...]  """ response =await self.extraction_client.chat.completions.create( model="gpt-4o-mini", messages=[{"role":"user","content": prompt}], temperature=0) scores = json.loads(response.choices[0].message.content)# Trier par score et garder top N scores.sort(key=lambda x: x["score"], reverse=True) best_ids =[s["passage_id"]-1for s in scores[:target]]return[chunks[i]for i in best_ids]
```

**Résultat attendu** :

* Contexte plus riche (20 chunks au lieu de 5)
* Sélection intelligente des 8 meilleurs
* +50% de complétude des réponses

***

### **#3. Enrichissement métadonnées Bible Notariale**

**Impact** : ⭐⭐⭐⭐⭐ (Débloque #6, #7, #10)
**Effort** : 0.5 jour

**Problème** : Les métadonnées de la Bible (lexique, questions typiques, vocabulaire spécifique) sont dans des JSON, pas dans Neo4j.

**Solution** :



python

```
# scripts/enrich_neo4j_from_bible.pyasyncdefenrich_neo4j_complete():"""Injecte TOUTES les métadonnées Bible dans Neo4j.""" metadata_dir = Path("_metadata/documents")for meta_file in metadata_dir.glob("*.metadata.json"): metadata = json.load(open(meta_file)) query ="""  MATCH (doc:Document {documentId: $doc_id})  SET  doc.categories_metier = $categories,  doc.type_document = $type,  doc.priorite = $priorite,  doc.mots_cles = $mots_cles,  doc.annee_reference = $annee,  doc.domaines_juridiques = $domaines,  doc.questions_typiques = $questions,  doc.vocabulaire_specifique = $vocab_spec,  doc.relations_documentaires = $relations  RETURN doc  """await neo4j.run(query,{"doc_id": metadata["document_id"],"categories": metadata.get("categories_metier",[]),"type": metadata["classification"]["type_document"],"priorite": metadata.get("priorite",5),"mots_cles": metadata["mots_cles"],"annee": metadata["classification"]["annee_reference"],"domaines": metadata["classification"]["domaines_juridiques"],"questions": metadata.get("questions_typiques",[]),"vocab_spec": json.dumps(metadata.get("vocabulaire_specifique",[])),"relations": json.dumps(metadata.get("relations_documentaires",{}))})print(f"✅ {len(list(metadata_dir.glob('*.metadata.json')))} documents enrichis")
```

**Résultat attendu** :

* 234 documents avec métadonnées complètes dans Neo4j
* Débloque toutes les optimisations Bible (#6, #7, #10)
* Base solide pour évolutions futures

***

### **#4. Prompt système avec expertise notariale**

**Impact** : ⭐⭐⭐⭐ (+35% qualité juridique)
**Effort** : 0.5 jour

**Problème** : Prompt générique, pas calibré sur le vocabulaire et les exigences du métier notarial.

**Solution** :



python

```
# backend/app/services/notaria_rag_service.pySYSTEM_PROMPT_NOTARIAL =""" Tu es un assistant juridique expert en droit notarial français, spécialisé dans le conseil aux notaires. MÉTHODOLOGIE DE RÉPONSE (OBLIGATOIRE) : 1. ANALYSE : Identifier la thématique juridique (déontologie, immobilier, RH, etc.) 2. PRINCIPES : Énoncer les principes juridiques applicables [avec Passage X] 3. RÈGLES : Détailler les règles spécifiques [avec Passage X] 4. EXCEPTIONS : Mentionner les exceptions ou cas particuliers si applicable 5. CONSÉQUENCES : Évoquer les risques/sanctions si pertinent 6. CONSEIL : Conclure par un conseil pratique orienté action RÈGLES STRICTES : - TOUJOURS vérifier s'il existe un conflit d'intérêts potentiel dans les questions déontologiques - TOUJOURS citer les sanctions disciplinaires si la question concerne une obligation - JAMAIS inventer d'information (hallucination = faute grave) - Si information partielle : "Les documents mentionnent [X] mais ne précisent pas [Y]." - Si hors périmètre : "Cette question relève de [domaine]. Je recommande de consulter [expert]." VOCABULAIRE NOTARIAL REQUIS : - "RPN" (Règlement Professionnel National), pas "règlement" - "Office notarial", pas "étude" ou "cabinet" - "Instrumenter" pour recevoir un acte authentique - "Minute" pour l'original de l'acte - "Expédition" pour la copie délivrée - "Émoluments" pour la tarification réglementée - "Honoraires" pour la rémunération libre STRUCTURE DE CITATION : - Format : [Passage X] après chaque affirmation basée sur un document - Minimum 1 citation par paragraphe - Citations précises, jamais vagues """asyncdef_synthesize_answer(self, question:str, chunks: List)->str:"""Génération avec prompt expert.""" context_str ="\n\n".join([f"[Passage {i+1}]\nDocument: {chunk.document_title}\n{chunk.text}"for i, chunk inenumerate(chunks)]) prompt =f"""{SYSTEM_PROMPT_NOTARIAL}PASSAGES EXTRAITS : {context_str}QUESTION : {question}RÉPONSE STRUCTURÉE (suivre la méthodologie ci-dessus) :"""# Code génération existant...
```

**Résultat attendu** :

* Vocabulaire notarial correct
* Structure juridique des réponses
* Mention systématique des risques/sanctions
* +35% de qualité perçue par les notaires

***

### **#5. Détection hors périmètre**

**Impact** : ⭐⭐⭐⭐ (100% faux positifs éliminés)
**Effort** : 1 jour

**Problème** :

* TEST\_HORSPER\_001 : "Puis-je monter une SCI" → répond au lieu de refuser
* TEST\_HORSPER\_002 : "Capitale de France" → cherche dans docs au lieu de répondre directement

**Solution** :



python

```
# backend/app/services/notaria_rag_service.pyasyncdefquery(self, question:str)->str:"""Point d'entrée avec détection hors périmètre."""# NOUVEAU : Classifier le scope AVANT tout traitement scope =await self._classify_question_scope(question)if scope =="CONNAISSANCE_GENERALE":returnawait self._answer_general_knowledge(question)elif scope =="CONSEIL_PERSONNALISE":return self._refuse_conseil_personnalise()elif scope =="HORS_PERIMETRE":return self._refuse_hors_perimetre(question)else:# PERIMETRE_NOTARIALreturnawait self._full_rag_pipeline(question)asyncdef_classify_question_scope(self, question:str)->str:"""Classifie en 4 scopes.""" prompt =f"""  Classifie cette question en UNE catégorie :  1. PERIMETRE_NOTARIAL  → Question sur déontologie, CCN, procédure notariale, réglementation profession  → Exemples : "Qu'est-ce que le RPN ?", "Obligations LCB-FT ?", "Avenant 59 CCN ?"  2. CONNAISSANCE_GENERALE  → Question de culture générale, définition courante, fait établi  → Exemples : "Capitale de France ?", "Qu'est-ce qu'une SAS ?", "Définition contrat ?"  3. CONSEIL_PERSONNALISE  → Question demandant un avis sur un cas spécifique client  → Exemples : "Puis-je accepter ce mandat ?", "Dois-je refuser ce dossier ?"  4. HORS_PERIMETRE  → Question sans rapport avec le notariat  → Exemples : "Recette tarte aux pommes ?", "Météo demain ?"  Question: {question} Réponds UNIQUEMENT le nom de la catégorie.  """ response =await self.extraction_client.chat.completions.create( model="gpt-4o-mini", messages=[{"role":"user","content": prompt}], temperature=0)return response.choices[0].message.content.strip()asyncdef_answer_general_knowledge(self, question:str)->str:"""Répond directement sans chercher dans les documents.""" response =await self.synthesis_client.chat.completions.create( model="gpt-4o", messages=[{"role":"system","content":"Tu es un assistant. Réponds brièvement et factuellement."},{"role":"user","content": question}], temperature=0)return response.choices[0].message.content def_refuse_conseil_personnalise(self)->str:return"""  Je fournis des informations réglementaires et documentaires sur le notariat,  mais je ne peux pas donner de conseil personnalisé sur des cas clients spécifiques.  Pour une situation particulière, je vous recommande de :  - Consulter votre Chambre interdépartementale  - Contacter le service juridique du CSN  - Échanger avec un confrère spécialisé  """def_refuse_hors_perimetre(self, question:str)->str:return"""  Cette question ne relève pas du périmètre de mes connaissances documentaires  sur le notariat français (déontologie, CCN, procédures professionnelles).  Je peux vous aider sur des questions concernant :  - La déontologie notariale (RPN, secret professionnel, conflits)  - La Convention Collective Nationale  - Les procédures professionnelles  - Les obligations réglementaires (LCB-FT, médiation, etc.)  """
```

**Résultat attendu** :

* 0 faux positifs hors périmètre
* Réponses directes sur connaissances générales
* Refus polis et orientés sur conseils personnalisés

***

## ⚡ OPTIMISATIONS RAPIDES (2.5 jours) - Gains marginaux importants

### **#6. Expansion de requête avec lexique notarial**

**Impact** : ⭐⭐⭐⭐ (+30% recall)
**Effort** : 0.5 jour

**Solution** :



python

```
# backend/app/services/query_expander.pyclassQueryExpander:def__init__(self):withopen('_metadata/vocabulaire_notarial.json')as f: self.lexique = json.load(f)defexpand(self, query:str)->str:"""  LCB-FT → "LCB-FT Lutte Contre Blanchiment Financement Terrorisme LAB"  CCN → "CCN Convention Collective Nationale IDCC 2205"  """ expanded =[query]for acronyme, expansion in self.lexique.items():if acronyme.lower()in query.lower():ifisinstance(expansion,str): expanded.append(expansion)elifisinstance(expansion,list): expanded.extend(expansion)return" ".join(expanded)# Intégrationasyncdef_reasoning_step(self, question:str): expanded_query = self.query_expander.expand(question) chunks =await self.neo4j.hybrid_search(query=expanded_query,...)
```

***

### **#7. Boost sémantique questions typiques**

**Impact** : ⭐⭐⭐⭐ (+25% précision ranking)
**Effort** : 1 jour

**Solution** :



python

```
# backend/app/services/question_matcher.pyasyncdefcompute_boost(user_q:str, doc_meta:dict)->float:"""Compare avec questions typiques du document."""ifnot doc_meta.get('questions_typiques'):return1.0 user_emb =await get_embedding(user_q) max_sim =0.0for typical_q in doc_meta['questions_typiques']: typical_emb =await get_embedding(typical_q) sim = cosine_similarity(user_emb, typical_emb) max_sim =max(max_sim, sim)return1.0+ max_sim # Boost 1.0 à 2.0# Intégrer dans rerankingasyncdef_rerank_with_llm(self, question, chunks, target=8): llm_scores =await self._llm_rerank(question, chunks) final_scores =[]for chunk, score inzip(chunks, llm_scores): doc_meta =await self._get_doc_metadata(chunk.document_id) boost =await self.question_matcher.compute_boost(question, doc_meta) final_scores.append((chunk, score * boost)) final_scores.sort(key=lambda x: x[1], reverse=True)return[chunk for chunk, _ in final_scores[:target]]
```

***

### **#8. Caching embeddings**

**Impact** : ⭐⭐⭐ (-40% temps sur requêtes similaires)
**Effort** : 0.5 jour

**Solution** :



python

```
import redis from hashlib import sha256 redis_client = redis.Redis(host='localhost', port=6379, db=0)asyncdefget_or_create_embedding(text:str): cache_key =f"emb:{sha256(text.encode()).hexdigest()}" cached = redis_client.get(cache_key)if cached:return json.loads(cached) embedding =await openai_client.embeddings.create(...) redis_client.setex(cache_key,86400, json.dumps(embedding))return embedding
```

***

### **#9. Parallélisation recherche**

**Impact** : ⭐⭐⭐ (-25% temps)
**Effort** : 0.5 jour

**Solution** :



python

```
import asyncio # Au lieu de séquentielvector_results, fulltext_results =await asyncio.gather( self.vector_search(...), self.fulltext_search(...))
```

***

## 🟢 OPTIMISATIONS MOYENNES (3 jours) - Si <80% après priorités

### **#10. Boost vocabulaire spécifique**

**Impact** : ⭐⭐⭐ (+15% pertinence)
**Effort** : 0.5 jour

**Solution** :



python

```
asyncdefapply_term_boosting(chunks, metadata_by_doc):for chunk in chunks: doc_meta = metadata_by_doc[chunk.document_id] vocab_spec = doc_meta.get('vocabulaire_specifique',[]) boost =1.0for term_info in vocab_spec:if term_info['terme'].lower()in chunk.text.lower(): boost *=1.5for syn in term_info.get('synonymes',[]):if syn.lower()in chunk.text.lower(): boost *=1.3 chunk.score *= boost returnsorted(chunks, key=lambda x: x.score, reverse=True)
```

***

### **#11. Graph traversal relations documentaires**

**Impact** : ⭐⭐⭐⭐ (+40% sur multi-docs)
**Effort** : 1.5 jour

**Solution** :



python

```
asyncdeffind_related_docs(doc_ids: List[str])-> List[str]:"""  Avenant 59 "modifie" Article 29.5  → Si on trouve Avenant 59, on récupère aussi Article 29.5 original  """ related_ids =set(doc_ids)for doc_id in doc_ids: metadata =await get_doc_metadata(doc_id) relations = metadata.get('relations_documentaires',{})for rel_type, related_list in relations.items(): related_ids.update(related_list)returnlist(related_ids)# Intégrer pour questions multi-documentsif is_multi_document_question(question): initial_doc_ids ={c.document_id for c in chunks[:5]} related_doc_ids =await find_related_docs(list(initial_doc_ids)) additional_chunks =await neo4j.hybrid_search( query=question, document_filter=related_doc_ids, top_k=10) chunks = chunks + additional_chunks
```

***

## 🟡 LONG TERME (3.5 jours) - Si vraiment nécessaire

### **#12. Graph traversal entités**

**Impact** : ⭐⭐⭐ (+30% précision factuelles)
**Effort** : 2 jours

**Solution** :



python

```
# Si trouve "Contrat Cyber MMA", récupérer automatiquement# toutes les franchises, dates, numéros liésMATCH (chunk)-[:HAS_ENTITY]->(entity:Organization {name:"MMA IARD"})MATCH (entity)<-[:HAS_ENTITY]-(related_chunk)WHERE related_chunk.text CONTAINS "échéance" OR related_chunk.text CONTAINS "franchise"RETURN related_chunk
```

***

### **#13. Chunking avec overlap**

**Impact** : ⭐⭐⭐ (+20% cohérence)
**Effort** : 1.5 jour (re-indexation)

**Solution** :



python

```
CHUNK_SIZE =512CHUNK_OVERLAP =100# 20% overlapchunk_with_context =f""" [Document: {doc_title}] [Section: {section_name}] {chunk_text}[Fin de chunk - Document: {doc_title}] """
```



[Analyse Graph](file:///workspace/1069f0be-6b6a-4c78-b854-f8b5330ffa8b/hXKmkA7RXf2Ms_TUPYOzZ)

[Grammaire notariale](file:///workspace/1069f0be-6b6a-4c78-b854-f8b5330ffa8b/zcvDAIAB8v5f30rqoWJrK)

[UI de Recherche & Knowledge Base](file:///workspace/1069f0be-6b6a-4c78-b854-f8b5330ffa8b/jE5gFtIuYo2xiIbGyXIbk)

[notes](file:///workspace/1069f0be-6b6a-4c78-b854-f8b5330ffa8b/in0LqVIhFLQb7io7MKMYu)
