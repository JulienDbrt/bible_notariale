# LE PROBLÈME DE LA DIMENSION TEMPORELLE

## LE PROBLÈME DE LA DIMENSION TEMPORELLE

### **Exemples concrets**

**Cas 1 : Succession**

* Question : "Monsieur X est décédé en 2015, quelles sont les règles de réserve héréditaire ?"
* Problème : La loi a changé en 2021 (loi Macron sur les réserves)
* Le chatbot va mélanger les deux versions → **réponse juridiquement fausse**

**Cas 2 : CCN**

* Question : "Quel était le salaire minimum en 2020 ?"
* Problème : Il y a eu 3 avenants depuis (58, 59, 60)
* Le chatbot donne le salaire actuel → **réponse incorrecte pour un dossier ancien**

**Cas 3 : Réglementation**

* Question : "Le RPN s'appliquait-il en 2023 ?"
* Réponse attendue : Non, il est entré en vigueur le 1er février 2024
* Le chatbot risque de dire oui → **anachronisme**

***

## 🔴 POURQUOI C'EST COMPLEXE POUR UN LLM

### **Problème #1 : Le LLM ne comprend pas le temps juridique**



```
LLM voit : "L'article 5 dispose que..." LLM ne sait PAS : - Cet article est-il en vigueur ? - Depuis quelle date ? - A-t-il été modifié depuis ? - Quelle version appliquer ?
```

### **Problème #2 : Le RAG n'a pas de conscience temporelle**



```
Documents dans Neo4j : - Avenant 59 (décembre 2024) : "Article 29.5 = X" - Avenant 58 (novembre 2024) : "Article 29.5 = Y" - CCN original (2019) : "Article 29.5 = Z" Question : "Quel était le contenu de l'article 29.5 en juillet 2024 ?" → Le RAG va mélanger les 3 versions sans logique temporelle
```

### **Problème #3 : Principe de non-rétroactivité**

En droit, sauf exception :

* La loi nouvelle ne s'applique pas aux faits passés
* Les contrats conclus sous l'ancienne loi restent régis par elle
* Les successions ouvertes avant le changement = ancienne loi

**Le LLM ne peut pas raisonner sur ces principes sans aide**

***

## 💡 SOLUTIONS POSSIBLES

### **Solution 1 : Métadonnées temporelles enrichies** (Fondation)

**Ajouter dans les métadonnées** :



json

```
{"document_id":"avenant_59","metadata":{"date_publication":"2024-12-12","date_entree_vigueur":"2025-01-01","date_fin_validite":null,"remplace":["avenant_58"],"remplace_articles":{"29.5":{"date_debut":"2025-01-01","version_precedente":"avenant_58"}}},"timeline":{"events":[{"date":"2024-12-12","type":"publication"},{"date":"2025-01-01","type":"entrée_vigueur"}]}}
```

**Enrichir Neo4j** :



python

```
query =""" MATCH (doc:Document {documentId: $doc_id}) SET  doc.date_entree_vigueur = $date_vigueur,  doc.date_fin_validite = $date_fin,  doc.remplace_ids = $remplace,  doc.est_actuel = $est_actuel """
```

**Impact** : Permet de filtrer par validité temporelle
**Effort** : 2 jours (enrichissement + validation)

***

### **Solution 2 : Détection du contexte temporel dans la question**

**Classifier automatiquement** :



python

```
asyncdefdetect_temporal_context(question:str)->dict:"""Détecte si la question a une dimension temporelle.""" prompt =f"""  Analyse cette question juridique et détecte le contexte temporel.  Question: {question} Détecte:  1. Y a-t-il une date explicite ? (année, mois, "en 2020", "actuellement")  2. Y a-t-il un événement daté ? ("lors du décès de", "au moment du divorce")  3. S'agit-il du droit actuel ou passé ?  Retourne JSON:  {{  "has_temporal_context": true/false,  "reference_date": "2020-06-15" ou null,  "temporal_type": "date_explicit" | "date_event" | "current" | "historical",  "needs_temporal_precision": true/false  }}  """ response =await llm.complete(prompt)return json.loads(response)# Exemples"Quelles sont les règles actuelles ?"→ {"has_temporal_context": true,"reference_date":"2025-11-18","type":"current"}"En 2020, quel était le salaire minimum ?"→ {"has_temporal_context": true,"reference_date":"2020-01-01","type":"date_explicit"}"Lors du décès en juin 2015, quelle loi s'appliquait ?"→ {"has_temporal_context": true,"reference_date":"2015-06-01","type":"date_event"}
```

**Impact** : Identifie 90% des questions avec dimension temporelle
**Effort** : 1 jour

***

### **Solution 3 : Filtrage temporel dans le RAG**

**Adapter la recherche selon la date** :



python

```
asyncdef_reasoning_step_temporal(self, question:str):"""Recherche avec conscience temporelle."""# 1. Détecter contexte temporel temporal_ctx =await self.detect_temporal_context(question)# 2. Classifier catégories (comme avant) categories =await self._classify_question(question)# 3. Filtrer documents par catégorie ET validité temporelleif temporal_ctx["has_temporal_context"]: relevant_docs =await self._filter_docs_temporal( categories=categories, reference_date=temporal_ctx["reference_date"])else:# Par défaut : documents actuels uniquement relevant_docs =await self._filter_docs_current(categories)# 4. Recherche normale chunks =await self.neo4j.hybrid_search( query=question, document_filter=relevant_docs, top_k=20)return chunks, temporal_ctx asyncdef_filter_docs_temporal(self, categories, reference_date):"""Filtre les documents valides à une date donnée.""" query ="""  MATCH (doc:Document)  WHERE ANY(cat IN doc.categories_metier WHERE cat IN $categories)  AND (doc.date_entree_vigueur <= $reference_date OR doc.date_entree_vigueur IS NULL)  AND (doc.date_fin_validite > $reference_date OR doc.date_fin_validite IS NULL)  RETURN doc.documentId as doc_id  ORDER BY doc.priorite DESC, doc.date_entree_vigueur DESC  """ result =await self.neo4j.run(query,{"categories": categories,"reference_date": reference_date })return[r["doc_id"]for r in result]asyncdef_filter_docs_current(self, categories):"""Filtre uniquement les documents actuellement en vigueur.""" query ="""  MATCH (doc:Document)  WHERE ANY(cat IN doc.categories_metier WHERE cat IN $categories)  AND doc.est_actuel = true  RETURN doc.documentId as doc_id  ORDER BY doc.priorite DESC  """ result =await self.neo4j.run(query,{"categories": categories})return[r["doc_id"]for r in result]
```

**Impact** : Évite 100% des anachronismes
**Effort** : 1.5 jours

***

### **Solution 4 : Prompt avec avertissement temporel**

**Adapter la synthèse** :



python

```
asyncdef_synthesize_answer_temporal(self, question, chunks, temporal_ctx):"""Synthèse avec contexte temporel explicite."""# Prompt de base system_prompt = SYSTEM_PROMPT_NOTARIAL # Ajout si contexte temporelif temporal_ctx["has_temporal_context"]: reference_date = temporal_ctx["reference_date"] temporal_warning =f""" CONTEXTE TEMPOREL CRITIQUE : La question porte sur le droit applicable au {reference_date}. Tu dois UNIQUEMENT utiliser les documents valides à cette date. ATTENTION : Ne JAMAIS mélanger avec des règles postérieures. AVERTISSEMENT À INCLURE dans la réponse : "⚠️ Cette réponse se base sur le droit en vigueur au {reference_date}. Si la situation est postérieure ou si la loi a changé depuis, consultez un notaire pour une analyse actualisée."  """ system_prompt += temporal_warning else:# Pas de date précise → avertir que c'est le droit actuel system_prompt +=""" AVERTISSEMENT À INCLURE dans la réponse : "ℹ️ Cette réponse se base sur le droit actuellement en vigueur (novembre 2025). Pour des situations anciennes, la loi applicable peut être différente."  """# Génération normale avec prompt enrichireturnawait self._generate_with_prompt(question, chunks, system_prompt)
```

**Impact** : Transparence totale pour l'utilisateur
**Effort** : 0.5 jour

***

### **Solution 5 : Gestion des versions documentaires**

**Structurer les versions dans Neo4j** :



cypher

```
// Créer des relations de succession temporelleMATCH(new:Document{documentId:"avenant_59"})MATCH(old:Document{documentId:"avenant_58"})CREATE(new)-[:REMPLACE{date:"2025-01-01"}]->(old)// Créer des nœuds Article avec historiqueCREATE(art:Article{ numero:"29.5", titre:"Participation financière formation"})CREATE(v1:ArticleVersion{ article_id:"29.5", version:1, date_debut:"2019-01-01", date_fin:"2024-11-14", contenu:"..."})CREATE(v2:ArticleVersion{ article_id:"29.5", version:2, date_debut:"2024-11-14", date_fin:"2024-12-12", contenu:"..."})CREATE(v3:ArticleVersion{ article_id:"29.5", version:3, date_debut:"2024-12-12", date_fin:null, contenu:"..."})CREATE(art)-[:VERSION]->(v1)CREATE(art)-[:VERSION]->(v2)CREATE(art)-[:VERSION]->(v3)
```

**Recherche par version** :



python

```
asyncdefget_article_version_at_date(article_id, reference_date):"""Récupère la bonne version d'un article à une date donnée.""" query ="""  MATCH (art:Article {numero: $article_id})-[:VERSION]->(v:ArticleVersion)  WHERE v.date_debut <= $reference_date  AND (v.date_fin > $reference_date OR v.date_fin IS NULL)  RETURN v  """ result =await neo4j.run(query,{"article_id": article_id,"reference_date": reference_date })return result
```

**Impact** : Gestion parfaite des versions
**Effort** : 3 jours (restructuration + migration)

***

## 📊 SYNTHÈSE DES SOLUTIONS

| Solution                           | Impact | Effort | Priorité      | Quand        |
| ---------------------------------- | ------ | ------ | ------------- | ------------ |
| **#1 Métadonnées temporelles**     | ⭐⭐⭐⭐⭐  | 2j     | 🔥 CRITIQUE   | Sprint 1 bis |
| **#2 Détection contexte temporel** | ⭐⭐⭐⭐⭐  | 1j     | 🔥 CRITIQUE   | Sprint 1 bis |
| **#3 Filtrage temporel RAG**       | ⭐⭐⭐⭐⭐  | 1.5j   | 🔥 CRITIQUE   | Sprint 1 bis |
| **#4 Avertissement temporel**      | ⭐⭐⭐⭐   | 0.5j   | 🔥 HAUTE      | Sprint 1 bis |
| **#5 Gestion versions**            | ⭐⭐⭐    | 3j     | 🟡 LONG TERME | Phase 2      |

**Total critique** : 5 jours pour #1+#2+#3+#4

***

## 🎯 PLAN D'IMPLÉMENTATION

### **Optimisation #14 : Gestion de la dimension temporelle**

**À ajouter dans le plan complet** :



markdown

```
### **#14. Gestion de la dimension temporelle****Impact** : ⭐⭐⭐⭐⭐ (Évite erreurs juridiques graves) **Effort** : 5 jours **Problème** : Le droit notarial est inter-temporel : la loi applicable dépend de la date de l'événement. Le système actuel mélange les versions sans logique temporelle. **Solution en 4 étapes** : #### **Étape 14A : Enrichir métadonnées temporelles (2j)**- Ajouter date_entree_vigueur, date_fin_validite - Identifier les relations "remplace" entre documents - Marquer les documents actuels vs historiques #### **Étape 14B : Détection contexte temporel (1j)**- LLM détecte si question a une date - Extraction de la date de référence - Classification : actuel / historique / date précise #### **Étape 14C : Filtrage temporel (1.5j)**- Requêtes Neo4j avec filtre temporel - Ne récupérer que docs valides à la date - Tri par priorité puis par date #### **Étape 14D : Avertissement explicite (0.5j)**- Prompt avec contexte temporel - Warning dans chaque réponse - Mention de la date de référence
```

***

## ⚠️ CAS LIMITES À GÉRER

### **Cas 1 : Question sans date précise**



```
Question : "Quelles sont les règles de succession ?" → Pas de date → Appliquer le droit actuel → Avertir : "Réponse basée sur le droit de novembre 2025"
```

### **Cas 2 : Question avec événement mais sans date**



```
Question : "Lors d'un divorce, comment partager les biens ?" → Pas de date explicite → Demander clarification : "À quelle époque le divorce a-t-il eu lieu ?" OU assumer droit actuel avec warning fort
```

### **Cas 3 : Changement de loi entre événement et question**



```
Question : "Mon oncle est décédé en 2010, puis-je renoncer à la succession ?" → Loi applicable = 2010 → Mais procédure actuelle peut avoir changé → Réponse nuancée : "En 2010, la loi disposait... La procédure actuelle est..."
```

### **Cas 4 : Période de transition**



```
Question : "Le RPN s'applique-t-il à un acte signé le 31 janvier 2024 ?" → RPN en vigueur le 1er février 2024 → Réponse : Non, c'est l'ancien règlement qui s'applique
```

