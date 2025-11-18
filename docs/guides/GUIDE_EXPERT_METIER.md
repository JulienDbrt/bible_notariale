# GUIDE EXPERT MÉTIER
## Validation du Chatbot Bible Notariale

**Version** : 1.0
**Date** : 18 novembre 2025

---

## VOTRE RÔLE

En tant qu'expert métier (notaire senior ou déontologue), votre expertise est essentielle pour valider la qualité du chatbot avant son déploiement.

**Votre mission** : Vérifier que les informations du chatbot sont juridiquement exactes et utilisables par les notaires.

**Temps requis** : 5 heures réparties sur 2 semaines (3 sessions)

---

## VUE D'ENSEMBLE DES 3 SESSIONS

| Session | Quand | Durée | Objectif |
|---------|-------|-------|----------|
| **1. Validation métadonnées** | Semaine 1 | 2h | Vérifier que les 234 documents sont bien classés |
| **2. Validation questions** | Semaine 1 | 1h30 | Vérifier que les questions de test sont réalistes |
| **3. Tests du chatbot** | Semaine 2 | 1h30 | Tester le chatbot en conditions réelles |

**Total** : 5h sur 2 semaines

---

## SESSION 1 : VALIDATION DES MÉTADONNÉES (2h)

### Contexte

Le système a automatiquement analysé 234 documents juridiques (RPN, CCN, circulaires, etc.) et leur a attribué :
- Un **type de document** (ex: Circulaire CSN, Règlement, Avenant CCN)
- Des **catégories métier** (ex: Déontologie, RH, Formation)
- Une **priorité** (1 à 10, où 10 = document critique)
- Des **mots-clés**

**Votre mission** : Vérifier sur un échantillon de 20 documents que cette classification automatique est correcte.

---

### Déroulement de la session

**Matériel fourni** :
- Un fichier Excel avec 20 documents à valider
- Accès aux PDF des documents

**Timing** :

| Étape | Durée | Description |
|-------|-------|-------------|
| Introduction | 10 min | Le chef de projet vous explique la méthode |
| Démonstration | 5 min | Vous validez ensemble 2 documents exemples |
| Validation | 75 min | Vous validez les 18 documents restants (5-6 min/doc) |
| Enrichissement | 20 min | Vous améliorez les mots-clés des documents prioritaires |
| Synthèse | 10 min | Vous identifiez les patterns d'erreur |

---

### Comment valider un document (5-6 minutes)

**Pour chaque document dans l'Excel** :

#### 1. Consulter le document source
- Le chef de projet ouvre le PDF sur un écran
- Vous parcourez rapidement le document (titre, sommaire, premiers paragraphes)

#### 2. Valider le TYPE de document

**Proposé par le système** : "Circulaire CSN"

**Votre réponse** :
- **"OK"** → Le chef de projet sélectionne "OK" dans l'Excel
- **"À corriger"** → Vous dictez le bon type (ex: "Règlement professionnel")

**Types de documents possibles** :
- Circulaire CSN
- Règlement professionnel
- Code de déontologie
- Avenant CCN
- Accord de branche
- Fil-Info
- Guide pratique
- Ordonnance/Décret
- Arrêté
- Autre

#### 3. Valider les CATÉGORIES métier

**Proposées par le système** : "Déontologie, Procédure"

**Votre réponse** :
- **"OK"** → Les catégories sont correctes
- **"À corriger"** → Vous dictez les bonnes catégories

**Catégories métier possibles** :
- DEONTOLOGIE
- RH (ressources humaines)
- FORMATION
- NEGOCIATION_IMMOBILIERE
- PROCEDURE
- TARIFICATION
- LCB_FT (Lutte contre le blanchiment)
- ASSURANCE
- ORGANISATION_PROFESSION
- AUTRE

#### 4. Valider la PRIORITÉ

**Proposée par le système** : "10" (document critique)

**Votre réponse** :
- **"OK"** → La priorité est correcte
- **"À corriger"** → Vous indiquez la bonne priorité (1 à 10)

**Échelle de priorité** :
- **10** : Documents critiques (RPN, Code déontologie, Circulaires majeures)
- **8-9** : Documents importants (Guides CSN, Avenants CCN majeurs)
- **5-7** : Documents utiles (Fil-Infos récents, Guides pratiques)
- **1-4** : Documents secondaires (Anciens Fil-Infos, documents obsolètes)

#### 5. Commentaires libres (optionnel)

Vous pouvez ajouter des remarques, par exemple :
- "Le document traite aussi de formation continue"
- "Attention, ce texte a été abrogé en 2024"
- "Document très technique, uniquement pour notaires expérimentés"

---

### Exemple concret

**Document** : `RPN_2024.pdf`

**Proposé par le système** :
- Type : "Règlement professionnel"
- Catégories : "Déontologie"
- Priorité : "10"
- Mots-clés : "RPN, secret professionnel, conflit d'intérêt"

**Votre validation** :
- Type : **OK** ✓
- Catégories : **À corriger** → "Déontologie, Procédure" (car le RPN couvre aussi les procédures)
- Priorité : **OK** ✓ (c'est bien un document priorité 10)
- Commentaires : "Document de référence absolue, à citer en priorité"

---

### Focus enrichissement (20 min en fin de session)

Pour les **10 documents priorité 10**, le chef de projet vous demandera :

**"Quels mots-clés importants manquent ?"**

Vous dictez les termes essentiels que les notaires cherchent fréquemment, par exemple :
- "médiation"
- "formation continue obligatoire"
- "délai de carence"
- "secret professionnel"
- "conflit d'intérêt"

**Objectif** : Améliorer la recherche documentaire du chatbot.

---

### Ce qu'on attend de vous

**Répondre rapidement** : 5-6 min par document maximum. Si vous hésitez, marquez "À corriger" et on y reviendra.

**Être pragmatique** : Pas besoin de lire le document en entier. Le titre, le sommaire et les premiers paragraphes suffisent.

**Signaler les anomalies graves** : Si un document est obsolète, mal nommé, ou ne devrait pas être dans la base.

---

## SESSION 2 : VALIDATION DES QUESTIONS (1h30)

### Contexte

Le système a généré 50 questions de test pour valider le chatbot. Nous allons en sélectionner 20 et vérifier qu'elles sont :
1. **Réalistes** : Ce sont des questions que posent vraiment les notaires
2. **Bien documentées** : Les documents sources sont corrects
3. **Exactes juridiquement** : Les réponses attendues sont correctes

---

### Déroulement de la session

**Matériel fourni** :
- Un fichier Excel avec 20 questions à valider
- Accès rapide aux documents sources

**Timing** :

| Étape | Durée | Description |
|-------|-------|-------------|
| Introduction | 10 min | Explication de la méthode |
| Validation | 60 min | Validation des 20 questions (3 min/question) |
| Enrichissement | 15 min | Affinage des réponses pour les questions pointues |
| Synthèse | 5 min | Retour d'expérience |

---

### Comment valider une question (3 minutes)

**Pour chaque question dans l'Excel** :

#### 1. Valider que la QUESTION est réaliste

**Exemple de question** : "Que signifie l'acronyme LCB-FT ?"

**Votre réponse** :
- **"Oui"** → C'est une vraie question que posent les notaires
- **"Non"** → Cette question n'est jamais posée en pratique
- **"À reformuler"** → L'idée est bonne mais la formulation est maladroite

**Si "À reformuler"**, vous dictez la bonne formulation, par exemple :
- Mauvaise : "C'est quoi la LCB-FT ?"
- Bonne : "Qu'est-ce que la LCB-FT et quelles sont les obligations du notaire ?"

#### 2. Valider les DOCUMENTS SOURCES

**Documents proposés** : `csn2019_analyse_lcb_ft.pdf`, `rpn_rpn.pdf`

**Votre réponse** :
- **"Oui"** → Ces documents permettent de répondre à la question
- **"Non"** → Les documents ne sont pas les bons
- **"Incomplet"** → Il manque un document

**Si "Incomplet"**, vous indiquez le(s) document(s) manquant(s).

#### 3. Valider les ÉLÉMENTS CLÉS de la réponse

**Éléments clés proposés** :
1. Lutte Contre le Blanchiment de capitaux
2. Financement du Terrorisme
3. Obligation légale pour les notaires

**Votre réponse** :
- **"Oui"** → Ces éléments sont complets et corrects
- **"Incomplet"** → Il manque un élément important (vous le dictez)
- **"Incorrect"** → Un élément est faux (vous le corrigez)

#### 4. Valider la RÉPONSE ATTENDUE

**Réponse proposée** : "LCB-FT signifie Lutte Contre le Blanchiment de capitaux et le Financement du Terrorisme..."

**Votre réponse** :
- **"Oui"** → La réponse est juridiquement exacte
- **"Non"** → La réponse contient une erreur juridique (vous la corrigez)
- **"À préciser"** → La réponse est trop vague (vous ajoutez des précisions)

**IMPORTANT** : C'est votre validation la plus critique. Toute inexactitude juridique doit être corrigée.

---

### Exemple concret

**Question** : "Quelles sont les cinq missions du notaire dans le serment ?"

**Validation** :

| Élément | Proposé | Votre réponse |
|---------|---------|---------------|
| **Question réaliste ?** | | **"À reformuler"** → "Quelles sont les missions mentionnées dans le serment du notaire ?" (car on ne dit pas forcément "cinq") |
| **Sources correctes ?** | `rpn_rpn.pdf` | **"Oui"** ✓ |
| **Éléments clés complets ?** | 1. Conseil 2. Rédaction 3. Authentification 4. Conservation 5. Exécution | **"Incomplet"** → Ajouter "6. Respect du secret professionnel" |
| **Réponse exacte ?** | "Les cinq missions sont..." | **"À préciser"** → "Il s'agit des missions de conseil, rédaction des actes, authentification, conservation des minutes, et exécution testamentaire, dans le respect du secret professionnel" |

---

### Ce qu'on attend de vous

**Être exigeant** : Si une réponse n'est pas juridiquement exacte à 100%, elle doit être corrigée.

**Penser "praticien"** : Les questions doivent refléter ce que demandent vraiment les notaires au quotidien.

**Enrichir les réponses pointues** : Pour les questions complexes, vos précisions sont essentielles.

---

## SESSION 3 : TESTS DU CHATBOT (1h30)

### Contexte

Maintenant que les métadonnées et les questions sont validées, vous allez tester le chatbot en conditions réelles.

**Objectif** : Vérifier que le chatbot répond correctement aux 20 questions validées.

---

### Déroulement de la session

**Matériel fourni** :
- Accès à l'interface du chatbot (navigateur web)
- Une liste de 20 questions à tester

**Timing** :

| Étape | Durée | Description |
|-------|-------|-------------|
| Présentation | 10 min | Découverte de l'interface chatbot |
| Démonstration | 5 min | Test d'une question ensemble |
| Tests individuels | 60 min | Vous testez ~7 questions individuellement |
| Débrief collectif | 15 min | Partage des observations |

---

### Comment tester une question (4-5 minutes)

#### 1. Choisir une question dans la liste

Vous cochez une question non testée dans le fichier Excel.

#### 2. Poser la question au chatbot

Vous tapez la question exactement comme elle est écrite (ou vous la reformulez naturellement).

#### 3. Lire la réponse complète

Prenez le temps de lire toute la réponse du chatbot.

#### 4. Donner votre feedback via le système "tribunal"

Vous utilisez le formulaire de feedback pour noter la réponse selon **3 critères notés sur 3** :

---

**A. EXACTITUDE /3**

Évalue la pertinence et la complétude de la réponse.

- **0/3** : Réponse incorrecte, hors sujet ou totalement incomplète
- **1/3** : Réponse partiellement correcte mais avec des erreurs importantes ou très incomplète
- **2/3** : Réponse correcte mais il manque des éléments importants
- **3/3** : Réponse complète, pertinente et exacte

**Critères** :
- La réponse répond-elle à la question posée ?
- Les informations juridiques sont-elles exactes ?
- Tous les éléments importants sont-ils présents ?

---

**B. SOURCES /3**

Évalue la pertinence et la complétude des sources citées.

- **0/3** : Aucune source ou sources totalement non pertinentes
- **1/3** : Sources partiellement pertinentes ou incomplètes
- **2/3** : Sources pertinentes mais il en manque une ou plusieurs importantes
- **3/3** : Sources parfaites (pertinentes et complètes)

**Critères** :
- Les documents cités sont-ils les bons ?
- Les sources permettent-elles de vérifier la réponse ?
- Manque-t-il une source importante ?

---

**C. FORMULATION /3**

Évalue la clarté, le style notarial et la longueur de la réponse.

- **0/3** : Réponse incompréhensible, trop longue ou inadaptée
- **1/3** : Réponse peu claire, style inapproprié ou longueur inadaptée
- **2/3** : Réponse claire mais peut être améliorée (style ou longueur)
- **3/3** : Formulation excellente (claire, professionnelle, longueur adaptée)

**Critères** :
- La réponse est-elle claire et compréhensible ?
- Le vocabulaire et le style sont-ils adaptés au notariat ?
- La longueur est-elle appropriée (ni trop courte, ni trop longue) ?

---

**D. Commentaire libre**

Notez vos observations précises, par exemple :
- "Très bonne réponse, claire et concise"
- "Il manque la référence au RPN article 5"
- "La date de publication est incorrecte (indique 2022 au lieu de 2024)"
- "Réponse trop verbeuse, peut être résumée en 2 paragraphes"
- "Parfait, exactement ce qu'un clerc a besoin de savoir"
- "Sources correctes mais réponse imprécise sur les délais"

#### 5. Cocher "Testée" dans l'Excel

#### 6. Passer à la question suivante

---

### Exemple de test

**Question testée** : "Que signifie l'acronyme LCB-FT ?"

**Réponse du chatbot** :
> "LCB-FT signifie Lutte Contre le Blanchiment de capitaux et le Financement du Terrorisme. Il s'agit d'obligations légales imposées aux notaires pour prévenir l'utilisation du système financier à des fins illégales. Ces obligations incluent la vérification de l'identité des clients, la déclaration de soupçon à TRACFIN, et la conservation des documents pendant 5 ans.
>
> Sources : Analyse nationale des risques LCB-FT (2019), RPN Article 12"

**Votre feedback** :

| Critère | Votre note | Explication |
|---------|------------|-------------|
| **EXACTITUDE** | **3/3** | Réponse complète et exacte (définition ✓, obligations ✓, détails pratiques ✓) |
| **SOURCES** | **3/3** | Les 2 documents cités sont pertinents (Analyse nationale + RPN) |
| **FORMULATION** | **3/3** | Claire, concise, vocabulaire adapté au notariat, longueur parfaite |
| **Commentaire** | "Parfait, très complet et pédagogique. Utile même pour un clerc débutant." |

**Score total** : 9/9 - Réponse excellente

---

### Ce qu'on attend de vous

**Être honnête** : Si la réponse est mauvaise, dites-le. C'est l'objectif du test.

**Être précis** : Dans les commentaires libres, expliquez ce qui ne va pas ou ce qui manque.

**Penser "utilisateur final"** : Imaginez qu'un clerc ou un notaire junior utilise cette réponse. Est-elle suffisante ?

**Noter les patterns** : Si plusieurs réponses ont le même problème (ex: dates incorrectes), signalez-le lors du débrief.

---

## APRÈS LES 3 SESSIONS : DÉCISION

Une réunion finale (2h, Semaine 2 - Vendredi) aura lieu pour décider si le chatbot peut passer en Phase 2 (déploiement élargi).

**Vous n'êtes pas obligé(e) d'y participer**, mais votre présence est fortement recommandée pour :
- Commenter les résultats
- Valider les recommandations d'amélioration
- Donner votre avis sur la pertinence du déploiement

**Grille de décision** :

| Résultat | Décision |
|----------|----------|
| ≥ 16/20 questions réussies + score moyen ≥ 3.5 | ✅ **GO** : Déploiement Phase 2 |
| 14-15/20 questions réussies | ⚠️ **ITÉRATION** : Corrections + re-tests |
| < 14/20 questions réussies | ❌ **STOP** : Revoir l'architecture |

---

## CONSEILS PRATIQUES

### Avant chaque session

- Bloquer le créneau complet (pas de rendez-vous juste après)
- Prévoir un café/thé
- Avoir accès à votre ordinateur (pour consulter les PDFs si besoin)

### Pendant les sessions

- N'hésitez pas à demander une pause si nécessaire
- Si vous ne savez pas : dites-le (mieux vaut vérifier que deviner)
- Si une question vous semble absurde : dites-le franchement

### Communication avec le chef de projet

Le chef de projet est là pour :
- Vous guider dans le processus
- Saisir vos réponses dans l'Excel
- Répondre aux questions techniques

**Vous ne devez PAS** :
- Manipuler l'Excel vous-même (sauf si vous le souhaitez)
- Chercher les documents (le chef de projet les ouvre pour vous)
- Vous inquiéter de la technique (c'est son rôle)

---

## FAQ

**Q : Dois-je vraiment lire chaque document en entier ?**
Non. Le titre, le sommaire et les premiers paragraphes suffisent généralement pour valider le type et les catégories.

**Q : Et si je ne connais pas un document ?**
Ce n'est pas grave. Basez-vous sur le contenu (titre, structure) pour valider le type et les catégories.

**Q : Puis-je proposer d'ajouter des documents manquants ?**
Oui ! Notez-le dans les commentaires libres.

**Q : Combien de temps entre chaque session ?**
Idéalement 2-3 jours pour que le chef de projet intègre vos corrections.

**Q : Que se passe-t-il si je trouve beaucoup d'erreurs ?**
C'est précisément l'objectif ! Si > 25% d'erreurs, le système d'annotation automatique sera corrigé.

**Q : Le chatbot va-t-il remplacer les notaires ?**
Non. C'est un outil d'aide à la décision pour les clercs et notaires juniors. Les cas complexes nécessitent toujours l'expertise d'un notaire senior.

---

## RESSOURCES

- Méthodologie complète : Demander au chef de projet
- Exemples de validation : Fournis lors de la démonstration
- Contact en cas de question : [Chef de projet]

---

**Merci pour votre contribution essentielle à la qualité de cet outil !**

**Votre expertise juridique est irremplaçable pour garantir la fiabilité du chatbot.**
