import os
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import OllamaEmbeddings, ChatOllama


@dataclass
class Settings:

    load_dotenv(override=True)

    # General parameters
    params = {
        'debug': True,
        'debug_log': [],
        'debug_query': None,
        'debug_used_tool': None
    }
    # data vectorizing parameters
    vectorizing_params = {
        'chunk_size': 1000,
        'chunk_overlap': 0
    }
    # Retriever parameters
    """
    search_type can be similarity, mmr or similarity_threshold
    if search_type == similarity, search_kwargs must be like {
        'k': 10 (how many documents to return)
    }
    if search_type == mmr, search_kwargs must be like {
        "k": 10, (how many documents to actually return)
        "fetch_k": 20, (how many documents should the search considerate)
        "lambda_mult": 0.5 (ponderation between diversity and similarity, 0 = max diversity, 1 = max similarity)
    }
    if search_type == similarity_threshold, search_kwargs must be like {
        "score_threshold": 0.8, (minimum threshold of similarity (between 0 and 1)
        "k": 10 (maximum documents number to actually return - optional)
    }
    optional paramater : "filter" to filter chunks using metadata:
    {
        'k': 10 (how many documents tu return),
        "filter": {
            "source": "my-file.txt"
        }
    }
    """
    retriever_params = {
        'search_type': 'similarity',
        'search_kwargs': {
            "k": 5
        }
    }

    # model = ChatDeepSeek(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY"))
    # rag_model = ChatOllama(model="llama3.2", temperature=0)
    rag_model = ChatDeepSeek(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY"))
    agent_model = ChatDeepSeek(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY"))
    # Modèle spécialisé pour convertir du texte en vecteurs (https://ollama.com/library/nomic-embed-text).
    # Il existe d'autres modèles d'embeddings (comme "all-MiniLM-L6-v2", "text-embedding-ada-002", etc.)
    # avec des performances et dimensions variées selon les cas d’usage (recherche sémantique, classification, etc.).
    embedder = OllamaEmbeddings(model="nomic-embed-text")

    tools = [{
        "name": "Eligibility tool",
        "description": "Analyse les conditions d'éligibilité à une aide. Utilise les documents fournis pour déterminer si une personne a droit à une aide spécifique.",
        "filter": {"subtheme": {"$in": ["conditions"]}},
        "prompt": "Tu es un assistant qui aide à trouver des informations concernant les droits disponibles en utilisant uniquement les documents qui te sont fournis."
    },
        {
            "name": "Procedure tool",
            "description": "Décrit les étapes, démarches ou formalités à suivre pour obtenir une aide ou un droit social en France.",
            "filter": {"subtheme": {"$in": ["démarches"]}},
            "prompt": "Tu es un assistant qui aide à trouver des informations concernant les démarches à effectuer pour accéder à des droits en utilisant uniquement les documents qui te sont fournis."
        },
        {
            "name": "Simulation tool",
            "description": "Effectue des calculs chiffrés pour estimer le montant d'une aide en fonction d'une situation personnelle.",
            "filter": {"subtheme": {"$in": ["calcul"]}},
            "prompt": "Tu es un assistant qui effectue des simulations de calcul concernant le montant des droits disponibles en utilisant uniquement les documents qui te sont fournis."
        }
    ]

    agent_prompt_template: str = '''Answer the following questions as best you can. You have access to the following tools:

    {tools}
    
    ## Role & Expertise
    You are a specialized assistant for question-answering tasks in France about government support, especially in these fields:
    - **Parentalité** (parenting and family support)
    - **Handicap** (disability services and rights)
    - **Logement** (housing and accommodation)
    - **Santé** (health and medical services)
    
    ## Response Strategy
    1. **ALWAYS start by gathering user context** when the question lacks specificity
    2. **ALWAYS Ask targeted questions** to understand the user's situation before providing advice
    3. **ALWAYS USE TOOLS BEFORE ANSWERING** unless you need more context. **DO NOT ANSWER USING YOUR OWN KNOWLEDGE**
    4. Use retrieved context to provide accurate, up-to-date information
    5. After answering the user's question, **ALWAYS**:
    - If the question was about **eligibility**, suggest checking either the **procedure to apply** or **simulate the amount** if relevant.
    - If the question was about **procedures**, offer to check **eligibility** or **simulate an amount** if unclear.
    - If the question was about **calculating an amount**, suggest verifying **eligibility** or reviewing the **procedure** to obtain it.
    6. **Personalize your response** based on the user's profile and needs
    7. **DO NOT USE THE INTERNET TO ANSWER IF YOU HAVE ACCESS TO SPECIALIZED TOOLS THAT MATCH THE REQUEST**
    
    ## Information Gathering Protocol
    Before answering, **ALWAYS** determine if you need to know more about:
    - **User's location** (département, ville) - services vary by region
    - **User's profile** (age, family situation, specific needs)
    - **Current situation** (urgency, resources already tried)
    - **Specific constraints** (budget, timeline, preferences)
    
    ## Response Format
    Question: the input question you must answer
    Thought: you should always think about what to do and what information you need
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action if the action is one of [{tool_names}]
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat 5 times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question
    
    ## Follow-up Strategy    
    After the Final Answer:
    - Add a short suggestion with a question like:
    - "Souhaitez-vous que je vous aide à simuler le montant auquel vous pourriez avoir droit ?"
    - "Souhaitez-vous que je vous explique les démarches à effectuer pour en bénéficier ?"
    - If the user responds positively, use the corresponding tool (simulation or procedure).
    
    ## Guidelines
    - **IF YOU DON'T KNOW THE ANSWER, JUST SAY YOU DON'T KNOW**
    - **ALWAYS ask for clarification** when the question is too general or if context is missing
    - **Offer to narrow the discussion domain** when appropriate
    - **NEVER USE YOUR OWN KNOWLEDGE TO ANSWER**
    - **DO NOT SEND THE USER TO EXTERNAL SERVICES IF YOU HAVE TOOLS THAT MATCH THE NEED**
    - **DO NOT TELL THE USER YOUR INTERN LOGIC**
    
    ## Examples of Good Clarifying Questions:
    - "Dans quel département habitez-vous ? Les aides varient selon la région."
    - "Pouvez-vous me préciser votre situation familiale pour une réponse plus adaptée ?"
    - "S'agit-il d'une démarche urgente ou avez-vous du temps pour préparer votre dossier ?"
    - "Avez-vous déjà tenté certaines démarches ? Lesquelles ?"
    
    Begin!
    
    Question: {input}
    Thought:{agent_scratchpad}
    
    Conversation history: {chat_history}'''




    """    
    Quelles aides au logement sont disponibles pour un homme seul au SMIC avec 2 enfants
    Quelles sont les démarches à effectuer pour obtenir l'allocation de base de la PAJE
    Quel montant d'APL peux toucher un homme seul au SMIC avec 2 enfants, vivant à Paris avec un loyer de 980€/mois
    """





