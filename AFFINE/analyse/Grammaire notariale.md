# Grammaire notariale

# PLAN D'AMÉLIORATION - TAXONOMIE MÉTIER & PERTINENCE DES RÉPONSES

## 🎯 OBJECTIF

Construire une **vraie grammaire métier notariale** basée sur l'analyse du corpus existant, pour améliorer la pertinence et l'adaptabilité des réponses du chatbot.

**Cible de performance :** Passer de <50% à 80% de satisfaction sur le corpus de test.

***

## 🔴 CONSTATS INITIAUX

### 1. Knowledge Graph : Trop plat, peu exploitable

**Problèmes identifiés :**

* Entités extraites sans discrimination → bruit informationnel majeur
* Pas de hiérarchie ni de typage (personnes = institutions = dates)
* Relations génériques non qualifiées
* Impossible d'utiliser comme base pour construire une taxonomie

**Conséquence :** Le graph actuel ne peut pas servir de fondation pour identifier les thématiques métier. Il faut partir du corpus textuel directement.

### 2. Adaptation métier insuffisante

**Trois problèmes structurants :**

| Dimension                  | Problème                                             | Impact                                              |
| -------------------------- | ---------------------------------------------------- | --------------------------------------------------- |
| **Prompts**                | Génériques, non calibrés sur le vocabulaire notarial | Ton inadapté, manque de précision juridique         |
| **Stratégie documentaire** | 234 docs utilisés en vrac, pas de hiérarchie         | Sources non pertinentes, dilution des résultats     |
| **Recherche**              | Paramètres non optimisés pour le jargon juridique    | Chunks pertinents manqués, bruit dans les résultats |

***

## 📊 MÉTHODOLOGIE : APPROCHE BOTTOM-UP

### Principe

Au lieu de **supposer** les catégories métier (approche top-down), les **découvrir** à partir du corpus existant (approche bottom-up), puis les valider avec l'expertise métier.

***

## 🔬 PHASE 1 : EXPLORATION SÉMANTIQUE DU CORPUS

### Objectif

Identifier les thématiques naturelles, le vocabulaire spécifique, et la structure hiérarchique des 234 documents.

### Méthodes d'analyse automatisée

#### 1.1. Extraction des termes discriminants

```
# TF-IDF sur les 234 documents
# Identifier les 100 termes les plus caractéristiques du vocabulaire notarial
# Exemples attendus : "minute", "instrumenter", "RPN", "déontologie", "mandat"

```

**Questions à résoudre :**

* Quels sont les 50 termes techniques les plus fréquents ?
* Quels termes distinguent la déontologie de l'immobilier ?
* Quels acronymes et abréviations sont utilisés ?

***

#### 1.2. Clustering thématique automatique

```
# Techniques : LDA (Latent Dirichlet Allocation) ou BERTopic
# Regrouper les documents en clusters naturels (5-10 attendus)
# Visualiser les distances sémantiques entre documents

```

**Questions à résoudre :**

* Combien de thématiques principales émergent naturellement ?
* Quels documents sont des outliers (non classifiables) ?
* Existe-t-il des sous-thématiques au sein des clusters principaux ?

**Output attendu :**

```
Cluster 1 : Déontologie & Discipline (45 docs)
  → Termes clés : RPN, secret professionnel, conflit intérêt, sanctions
  
Cluster 2 : Négociation Immobilière (28 docs)
  → Termes clés : mandat, honoraires, vente, acquéreur, vendeur
  
Cluster 3 : Procédures & Réclamations (18 docs)
  → Termes clés : médiation, conciliation, chambre, tribunal
  
Cluster 4 : Assurances & RCP (12 docs)
  → Termes clés : cyber, franchise, sinistre, MMA, garantie
  
Cluster 5 : RH & Convention Collective (15 docs)
  → Termes clés : salaire, congés, 13e mois, CSN, employeur
  
[...]

```

***

#### 1.3. Analyse des co-occurrences

```
# Identifier quels termes apparaissent ensemble
# Construire un graphe de concepts (différent du KG actuel)
# Exemple : "secret professionnel" co-occurre avec "RPN", "article 29", "sanctions"

```

**Questions à résoudre :**

* Quels concepts sont systématiquement liés ?
* Quelles sont les chaînes de raisonnement typiques ?
* Quels termes sont des synonymes pratiques ?

**Output attendu :**

```
"acte authentique" ↔ "instrumenter" ↔ "minute" ↔ "notaire instrumentaire"
"conflit d'intérêts" ↔ "indépendance" ↔ "impartialité" ↔ "article 29 RPN"
"franchise" ↔ "cyber" ↔ "sinistre" ↔ "MMA IARD"

```

***

#### 1.4. Hiérarchie documentaire par autorité

```
# Analyse de la structure des citations
# Documents les plus cités → autorité forte
# Documents récents citant les anciens → hiérarchie temporelle

```

**Questions à résoudre :**

* Quels sont les 5 documents "sources primaires" les plus référencés ?
* Quelle est la hiérarchie naturelle : réglementaire > guide > newsletter ?
* Quels documents sont orphelins (jamais cités) ?

**Output attendu :**

```
Niveau 1 - Sources réglementaires (autorité max)
  → RPN, Code pénal, Décret 1973, Règlement Cour

Niveau 2 - Guides officiels
  → Guide négociation immobilière CSN, Vade-mecum

Niveau 3 - Documents opérationnels
  → Contrats types, Fiches pratiques

Niveau 4 - Actualités et newsletters
  → Fil-info, Alertes juridiques

Niveau 5 - Documents ad hoc
  → Q&R clients, Notes internes

```

***

### Livrables Phase 1

| Livrable                      | Description                                           | Format                  |
| ----------------------------- | ----------------------------------------------------- | ----------------------- |
| **Carte sémantique**          | Visualisation interactive des thématiques découvertes | HTML interactif (D3.js) |
| **Matrice de co-occurrences** | Termes techniques et leurs associations               | CSV + heatmap           |
| **Clusters documentaires**    | Classification automatique des 234 docs               | JSON avec scores        |
| **Hiérarchie d'autorité**     | Graphe de citations entre documents                   | Cypher Neo4j            |

**Durée estimée :** 3-4 jours (développement + exécution analyses)

***

## ✅ PHASE 2 : VALIDATION MÉTIER

### Objectif

Confronter les découvertes automatiques à l'expertise notariale pour corriger, affiner et enrichir.

### Méthodologie

#### 2.1. Workshop de validation (2-3h)

**Participants :** Delphine Cudelou + 1-2 notaires de l'équipe

**Agenda :**

1. **Présentation des clusters découverts** (30 min)
   * Montrer la carte sémantique
   * Expliquer les 5-8 thématiques principales
   * Identifier les documents mal classés
2. **Validation de la taxonomie** (45 min)
   * Confirmer ou renommer les catégories
   * Ajouter les sous-catégories manquantes
   * Définir les frontières entre thématiques
3. **Dictionnaire notarial** (30 min)
   * Valider les termes techniques extraits
   * Ajouter les synonymes métier
   * Identifier les faux-amis (homonymes juridiques)
4. **Hiérarchie des sources** (30 min)
   * Confirmer l'ordre d'autorité proposé
   * Ajuster les niveaux de priorité
   * Identifier les documents manquants critiques
5. **Templates de réponse** (30 min)
   * Définir le ton attendu par catégorie
   * Spécifier les éléments obligatoires (sources, sanctions, etc.)
   * Établir les règles de prudence (quand ne pas répondre)

***

#### 2.2. Ajustements post-workshop

**Actions immédiates :**

1. Corriger la classification automatique selon feedback métier
2. Enrichir le dictionnaire avec les termes manqués
3. Affiner la hiérarchie d'autorité
4. Documenter les cas limites et zones grises

**Output :**

```
# Taxonomie Validée - Chatbot Notaires Caen

## Catégories Principales (6)

### 1. DÉONTOLOGIE & DISCIPLINE
**Périmètre :** Secret professionnel, conflits d'intérêts, sanctions, honoraires, exercice professionnel
**Sources prioritaires :** RPN, Code pénal art. 226-13, Décret 1973
**Ton requis :** Autoritaire, prudent, références obligatoires
**Template réponse :**
> "En matière de déontologie, l'article [X] du RPN dispose que [règle]. 
> Le non-respect expose le notaire à [sanction]. 
> En cas de doute, consulter la Chambre interdépartementale."

### 2. NÉGOCIATION IMMOBILIÈRE
**Périmètre :** Mandat de vente, honoraires négo, délégation, agences
**Sources prioritaires :** Guide CSN, Loi Hoguet, RPN art. négo
**Ton requis :** Procédural, étapes détaillées, délais précis
**Template réponse :**
> "La procédure de négociation immobilière notariale comprend [étapes].
> Le mandat doit obligatoirement [conditions]. 
> Honoraires : [barème ou liberté selon cas]."

[... 4 autres catégories ...]

```

***

### Livrables Phase 2

| Livrable                          | Description                             |
| --------------------------------- | --------------------------------------- |
| **Taxonomie métier validée**      | 5-8 catégories avec périmètres définis  |
| **Dictionnaire notarial enrichi** | 200+ termes avec synonymes et relations |
| **Hiérarchie sources consolidée** | Niveau d'autorité 1-5 pour les 234 docs |
| **Templates de réponse**          | Structure type par catégorie métier     |

**Durée estimée :** 2-3 jours (workshop + ajustements)

***

## 🛠️ PHASE 3 : IMPLÉMENTATION TECHNIQUE

### Objectif

Intégrer les découvertes dans le système pour améliorer la pertinence des réponses.

### 3.1. Enrichissement des métadonnées Neo4j

**Ajouter aux documents :**

```
{
  "documentId": "rpn_2024",
  "title": "Règlement Professionnel National",
  "categorie": "DEONTOLOGIE",
  "sous_categorie": "secret_professionnel",
  "autorite": "REGLEMENTAIRE",
  "niveau_autorite": 10,
  "perimetre": "NATIONAL",
  "date_publication": "2024-01-15",
  "obsolete": false,
  "mots_cles": ["secret professionnel", "conflit intérêt", "sanctions"],
  "cite_par": ["guide_deonto_2024", "newsletter_mars_2024"],
  "cite": ["code_penal", "decret_1973"]
}

```

**Ajouter aux entités :**

```
{
  "entityId": "secret_professionnel",
  "type": "LegalConcept",
  "categorie": "DEONTOLOGIE",
  "niveau_priorite": 10,
  "synonymes": ["confidentialité notariale", "discrétion professionnelle"],
  "termes_lies": ["article_226_13", "RPN", "sanctions_disciplinaires"],
  "definition_courte": "Obligation absolue du notaire de ne divulguer aucune information..."
}

```

**Script de migration :**

```
# Appliquer les métadonnées à tous les documents existants
# Basé sur la classification validée en Phase 2
async def enrich_document_metadata():
    for doc_id, metadata in validated_taxonomy.items():
        await neo4j.run_query("""
            MATCH (doc:Document {documentId: $doc_id})
            SET doc.categorie = $categorie,
                doc.autorite = $autorite,
                doc.niveau_autorite = $niveau,
                doc.mots_cles = $mots_cles
        """, metadata)

```

***

### 3.2. Routing intelligent des requêtes

**Étape de classification pré-recherche :**

```
async def classify_and_route_query(question: str) -> QueryRoute:
    """
    Identifie la catégorie métier de la question avant la recherche.
    Route vers les documents pertinents uniquement.
    """
    
    prompt = f"""
    Classifie cette question notariale dans UNE catégorie principale.
    
    Catégories disponibles :
    - DEONTOLOGIE : Secret professionnel, conflits, sanctions, exercice
    - IMMOBILIER : Négociation, vente, mandat, honoraires
    - PROCEDURE : Médiation, réclamations, discipline, conciliation
    - ASSURANCES : RCP, cyber, sinistres, franchises
    - RH : Convention collective, salaires, congés
    - SUCCESSION : Donations, testaments, héritages
    
    Question : {question}
    
    Réponds en JSON :
    {{
      "categorie": "...",
      "termes_techniques": [...],
      "niveau_complexite": "simple|moyen|complexe"
    }}
    """
    
    classification = await llm_classify(prompt)
    
    # Récupérer les docs de cette catégorie avec autorité >= 7
    relevant_docs = await neo4j.run_query("""
        MATCH (doc:Document)
        WHERE doc.categorie = $categorie
          AND doc.niveau_autorite >= 7
          AND NOT doc.obsolete
        RETURN doc.documentId
        ORDER BY doc.niveau_autorite DESC
        LIMIT 50
    """, {"categorie": classification["categorie"]})
    
    return {
        "categorie": classification["categorie"],
        "target_documents": relevant_docs,
        "complexity": classification["niveau_complexite"]
    }

```

***

### 3.3. Prompts système spécialisés

**Créer un prompt par catégorie métier :**

```
PROMPT_TEMPLATES = {
    "DEONTOLOGIE": """
Tu es un assistant spécialisé en déontologie notariale.

RÈGLES STRICTES :
1. TOUJOURS citer l'article précis du RPN ou du Code pénal
2. TOUJOURS mentionner les sanctions disciplinaires applicables
3. Adopter un ton autoritaire et prudent
4. En cas de conflit d'intérêts potentiel, le signaler explicitement
5. Ne JAMAIS minimiser la gravité d'une faute déontologique

STRUCTURE DE RÉPONSE OBLIGATOIRE :
1. Principe juridique applicable [avec article RPN]
2. Règle(s) spécifique(s) [avec sources]
3. Exceptions éventuelles [si applicable]
4. Sanctions en cas de manquement [avec références]
5. Conseil prudent pour éviter le risque

PASSAGES FOURNIS :
{context}

QUESTION : {question}

RÉPONSE STRUCTURÉE :
""",

    "IMMOBILIER": """
Tu es un assistant spécialisé en négociation immobilière notariale.

RÈGLES STRICTES :
1. Détailler les étapes procédurales dans l'ordre chronologique
2. Préciser les délais réglementaires et conventionnels
3. Mentionner les documents obligatoires à fournir
4. Indiquer le régime des honoraires (réglementé ou libre)
5. Signaler les pièges et erreurs fréquentes

STRUCTURE DE RÉPONSE OBLIGATOIRE :
1. Cadre juridique [Loi Hoguet, RPN, Guide CSN]
2. Procédure détaillée [étapes numérotées]
3. Documents requis [liste exhaustive]
4. Honoraires applicables [barème ou liberté]
5. Points de vigilance [erreurs à éviter]

PASSAGES FOURNIS :
{context}

QUESTION : {question}

RÉPONSE STRUCTURÉE :
""",

    # ... Autres catégories
}

# Utiliser le prompt adapté selon la catégorie
async def synthesize_with_specialized_prompt(
    question: str, 
    context: str, 
    categorie: str
) -> str:
    prompt_template = PROMPT_TEMPLATES.get(categorie, PROMPT_TEMPLATES["DEFAULT"])
    prompt = prompt_template.format(context=context, question=question)
    
    return await llm_synthesis(prompt)

```

***

### 3.4. Dictionnaire juridique & Boost

**Enrichissement de la recherche vectorielle :**

```
# Dictionnaire de synonymes notariaux
LEGAL_SYNONYMS = {
    "acte authentique": ["acte notarié", "instrumentum", "minute authentique"],
    "secret professionnel": ["confidentialité", "discrétion professionnelle"],
    "conflit d'intérêts": ["conflit d'intérêt", "incompatibilité"],
    "RPN": ["Règlement Professionnel National", "règlement national"],
    "office notarial": ["étude notariale", "office"],
    # ... 200+ entrées
}

# Termes techniques avec boost de score
HIGH_VALUE_TERMS = {
    "RPN": 2.0,
    "article": 1.5,
    "secret professionnel": 2.0,
    "conflit d'intérêts": 2.0,
    "franchise": 1.8,
    "mandat": 1.8,
    "honoraires": 1.5,
    # ... 100+ termes
}

async def expand_query_with_synonyms(query: str) -> str:
    """Enrichit la requête avec les synonymes juridiques."""
    expanded_terms = []
    
    for term, synonyms in LEGAL_SYNONYMS.items():
        if term.lower() in query.lower():
            expanded_terms.extend(synonyms)
    
    return f"{query} {' '.join(expanded_terms)}"

async def apply_term_boosting(chunks: List[Chunk]) -> List[Chunk]:
    """Booste le score des chunks contenant des termes techniques."""
    for chunk in chunks:
        boost_factor = 1.0
        
        for term, boost in HIGH_VALUE_TERMS.items():
            if term.lower() in chunk.text.lower():
                boost_factor *= boost
        
        chunk.score *= boost_factor
    
    return sorted(chunks, key=lambda x: x.score, reverse=True)

```

***

### Livrables Phase 3

| Livrable                   | Description                                        |
| -------------------------- | -------------------------------------------------- |
| **Métadonnées enrichies**  | 234 documents avec catégorie, autorité, mots-clés  |
| **Routing intelligent**    | Classification automatique + filtrage documentaire |
| **Prompts spécialisés**    | 6 templates adaptés par catégorie métier           |
| **Dictionnaire juridique** | 200+ synonymes + 100+ termes boostés               |

**Durée estimée :** 4-5 jours (développement + tests)

***

## 📊 PHASE 4 : TESTS & VALIDATION

### 4.1. Tests A/B sur corpus

**Protocole :**

1. Prendre le corpus de 20 questions de test
2. Comparer version actuelle (baseline) vs version optimisée
3. Mesurer les métriques par question et en moyenne

**Métriques à tracker :**

| Métrique                    | Baseline | Après Optim | Objectif |
| --------------------------- | -------- | ----------- | -------- |
| **Précision des sources**   | 30%      | ?           | 80%      |
| **Complétude des réponses** | 40%      | ?           | 80%      |
| **Taux d'hallucination**    | 15%      | ?           | <5%      |
| **Score satisfaction /25**  | 15.5     | ?           | >21      |
| **Temps de réponse**        | 8s       | ?           | <5s      |

***

### 4.2. Analyse des échecs résiduels

**Pour chaque test échoué :**

1. Identifier la cause racine (source, prompt, recherche ?)
2. Proposer un ajustement ciblé
3. Re-tester après correction
4. Documenter le pattern d'échec

**Template d'analyse :**

```
## Test échoué : TEST_DEON_001

**Question :** Collaboratrice achète bien, vendeurs peuvent passer par ce notaire ?

**Réponse attendue :** Mention du conflit d'intérêts, alternatives (notaire tiers)

**Réponse obtenue :** Info sur négociation immo (hors sujet)

**Cause racine :** 
- Classification erronée : IMMOBILIER au lieu de DEONTOLOGIE
- Documents routés : Guide négo immo (incorrect)
- Documents manqués : RPN art. 29 (conflit d'intérêts)

**Correction appliquée :**
- Améliorer le prompt de classification (ajouter "conflit" comme trigger DEONTOLOGIE)
- Boost sur "conflit d'intérêts" dans le dictionnaire
- Ajout métadonnée "sous_categorie: conflit_interets" au RPN art. 29

**Résultat après correction :**
- Classification : DEONTOLOGIE ✓
- Documents routés : RPN, Règlement Cour ✓
- Réponse : Mentionne le conflit d'intérêts + alternatives ✓
- Score : 21/25 (vs 10/25 avant)

```

***

## 📅 PLANNING GLOBAL

### Vue d'ensemble

| Phase                                | Durée | Responsable             | Dépendances      |
| ------------------------------------ | ----- | ----------------------- | ---------------- |
| **Phase 1 : Exploration sémantique** | 3-4j  | Tech (Tristan)          | -                |
| **Phase 2 : Validation métier**      | 2-3j  | Delphine + Tech         | Phase 1 complète |
| **Phase 3 : Implémentation**         | 4-5j  | Tech (Tristan + Julien) | Phase 2 validée  |
| **Phase 4 : Tests & validation**     | 3-4j  | Delphine + Tech         | Phase 3 déployée |

**Durée totale :** 12-16 jours (2.5 à 3 semaines)

***

### Découpage par semaines

#### Semaine 1 : Exploration + Validation

* **J1-J3 :** Analyses automatisées du corpus (TF-IDF, clustering, co-occurrences)
* **J4 :** Préparation workshop (visualisations, synthèse)
* **J5 :** Workshop validation métier (2-3h) + ajustements post-workshop

**Livrable S1 :** Taxonomie validée + dictionnaire enrichi

***

#### Semaine 2 : Implémentation technique

* **J1-J2 :** Enrichissement métadonnées Neo4j + routing intelligent
* **J3-J4 :** Prompts spécialisés + dictionnaire juridique
* **J5 :** Tests unitaires + déploiement

**Livrable S2 :** Système optimisé déployé en environnement de test

***

#### Semaine 3 : Tests & Itérations

* **J1-J2 :** Tests A/B sur corpus de 20 questions
* **J3-J4 :** Analyse des échecs + corrections ciblées
* **J5 :** Validation finale + documentation

**Livrable S3 :** Rapport de validation avec métriques atteintes

***

## 🎯 CRITÈRES DE SUCCÈS

### Quantitatifs

* ✅ **≥80%** de questions jugées utiles (score ≥3/5)
* ✅ **≥80%** de précision des sources (bonnes sources utilisées)
* ✅ **<5%** de taux d'hallucination
* ✅ **<5s** de temps de réponse moyen
* ✅ **Score ≥21/25** en moyenne sur le corpus de test

### Qualitatifs

* ✅ Taxonomie métier validée par Delphine et l'équipe
* ✅ Prompts adaptés au vocabulaire notarial
* ✅ Routing documentaire intelligent et fiable
* ✅ Dictionnaire juridique complet et opérationnel
* ✅ Système maintenable et documenté

***

## 💡 POINTS D'ATTENTION

### Risques identifiés

| Risque                                | Impact | Mitigation                                     |
| ------------------------------------- | ------ | ---------------------------------------------- |
| **Clustering automatique incohérent** | Moyen  | Validation humaine systématique en Phase 2     |
| **Workshop non concluant**            | Fort   | Préparation soignée + questions ciblées        |
| **Surcharge métadonnées**             | Faible | Garder uniquement les métadonnées actionnables |
| **Dictionnaire incomplet**            | Moyen  | Enrichissement itératif post-déploiement       |

### Dépendances critiques

1. **Disponibilité Delphine** pour workshop (Phase 2 bloquante)
2. **Qualité du corpus** : 234 docs suffisants et représentatifs ?
3. **Puissance Neo4j** : Peut gérer les métadonnées enrichies ?

***

## 📚 ANNEXES

### Outils techniques utilisés

* **Clustering :** Scikit-learn (LDA) ou BERTopic
* **TF-IDF :** Scikit-learn TfidfVectorizer
* **Visualisation :** Plotly / D3.js pour cartes sémantiques
* **Neo4j :** Cypher pour enrichissement métadonnées

### Ressources documentaires

* Guide CSN sur la négociation immobilière
* RPN (Règlement Professionnel National)
* Décret n°73-609 du 5 juillet 1973
* Convention collective du notariat

***

**Document de travail - Version consolidée**
*À mettre à jour au fil de l'avancement du projet*

[](file:///workspace/1069f0be-6b6a-4c78-b854-f8b5330ffa8b/r80gClLybwwB4nyzdhk5j)
