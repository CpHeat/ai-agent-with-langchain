
# 🤖 agent IA citoyen (ChatBot) avec langchain 

Ce projet vise à concevoir un assistant conversationnel intelligent capable de répondre en langage naturel à des questions portant sur les droits sociaux et administratifs, à partir de documents institutionnels publics.

 Il utilise les outils LangChain, une architecture RAG pour la recherche contextuelle, un agent IA pour la gestion des outils personnalisés, une mémoire conversationnelle pour maintenir le fil du dialogue, et une interface Streamlit claire et fluide.

Ce projet a été réalisé par [Charle](https://github.com/CpHeat), [Louis](https://github.com/lougail) et [Sayana](https://github.com/sayana-project) lors de la formation Dev IA chez Simplon HDF-Lille.

- Pour en savoir plus sur les agent IA, consultez [cette page Wikipedia](https://fr.wikipedia.org/wiki/Agent_intelligent).

**🎯 Objectif du projet**

Ce prototype simule un assistant numérique dans un contexte réel de service public, permettant à un citoyen de :

Trouver des informations claires et contextualisées sur ses droits (ex. aides au logement, handicap, aides à l'enfance).

Poser des questions complexes (ex. éligibilité, résumé de procédures).

Utiliser des outils intégrés (résumé, simplification, évaluation d’éligibilité).

Restreindre la recherche à un domaine pour améliorer la pertinence.

Dialoguer facilement via une interface web.

Ce projet est réalisé dans le cadre de la formation Dev IA – Simplon HDF - Lille.
## 🏗️ Architecture & Composants IA

1. RAG (Retrieval-Augmented Generation)
- Recherche dans des documents vectorisés (ChromaDB).

- Fournit des sources fiables aux réponses.

2. Agent IA (LangChain Agent)
- Analyse la requête.

- Utilise les outils personnalisés (résumé, simplification, éligibilité).

- Coordination avec la mémoire et la base documentaire.

3. Mémoire conversationnelle
- Maintient le contexte de la discussion.

- Permet des interactions naturelles et suivies.

4. Interface utilisateur (Streamlit)
- Permet au citoyen d'interagir avec l'assistant.

- Proposition automatique de restreindre un domaine de recherche.

- UI pensée pour la clarté, l'accessibilité et la fluidité.
## Arborescence du projet

Voici l'aborescence du projet pour mieux localiser certains fichiers : 

- **data/** : Dossier contenant les documents d'information sur les aides et droits français.
  - **`aide au logement/** : Dossier contenant les documents d'aide au logement.
  - **handicap/** : Dossier contenant les documents d'aide pour handicapé.
  - **enfant/** : Dossier contenant les documents d'aide au enfant.
- **db/** : Dossier contenant la vectorisation des documents en db.
  - **chroma.sqlite3** : Fichier query de la DB.
  - **de55fs45119gd5**: Vecorisation des documents.
- **main.py** : Point d'entrée de l'application.
- **settings.py** : Fichier paramétre de l'application.
- **rag.ypynb**: Notebook sur le RAG
- **agent.ypynb**: Notebook sur l'agent IA
- **interface.py** : Fichier pour la classe représentant une planète.
- **README.md** : Documentation du projet.
## Pré-requis et installation 

**Récupére le projet chatbot**
```bash
git clone https://github.com/CpHeat/ai-agent-with-langchain.git
```
**Installer les dépendances**
```bash
pip install -r requirements.txt
```
**Lancer l’interface utilisateur**
```python
streamlit run main.py
```
## 📄 Thème choisi

**Accès aux droits** : notre assistant se concentre sur la compréhension des droits sociaux et administratifs dans les domaines suivants :

- Aides au logement

- Aides pour personnes en situation de handicap

- Aides pour familles et enfants
## 👥 Contributions des membres de l'équipe
- **[Charle](https://github.com/CpHeat)**:
  - Récupération des données & structuration des dossiers

  - Vectorisation et mise en place du système RAG

  - Coordination entre RAG et agent

  - Refactorisation et clarté du code
    
- **[Louis](https://github.com/lougail)**: 
    - Développement de l’interface Streamlit (UI/UX)
    - Intégration de l’agent IA dans l’interface
    - Tests de communication avec le backend IA

- **[Sayana](https://github.com/sayana-project)**: 
    - Implémentation de l’agent conversationnel
    - Prompting, mémoire conversationnelle
    - Création et intégration des outils personnalisés
## License

[MIT](https://choosealicense.com/licenses/mit/)

