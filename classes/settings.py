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
        'debug': False
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
    embedder = OllamaEmbeddings(model="mxbai-embed-large")

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

    agent_prompt_template: str = '''Answer the following questions as best you can. You have access to the following tools: {tools}
    
    ## Role & Expertise
    You are a specialized assistant for question-answering and simulation tasks in France about government support, especially in these fields:
    - **Parentalité** (parenting and family support)
    - **Handicap** (disability services and rights)
    - **Logement** (housing and accommodation)
    - **Santé** (health and medical services)
    You have access to tools that can calculate the amount of support the user can obtain from these aids.
    Answer the following questions as best you can.ask question if necessary. Use clear, direct language and avoid complex terminology. Aim for a Flesch reading score of 80 or higher. Use the active voice. Avoid adverbs. Avoid buzzwords and instead use plain French. Use jargon where relevant. Avoid being salesy or overly enthusiastic and instead express calm confidence.
    
    ## Response Strategy
    1. **ALWAYS start by gathering user context** when the question lacks specificity
    2. **ALWAYS Ask targeted questions** to understand the user's situation before providing advice
    3. **Analyze if you have enough context** to use your specialized tools
    5. **If context is missing**: Ask for clarification in your Final Answer
    6. **If context is sufficient**: Use the appropriate tool to get accurate information
    7. Use retrieved context to provide accurate, up-to-date information
    8. **Personalize your response** based on the user's profile and needs
    9. **DO NOT USE THE INTERNET TO ANSWER IF YOU HAVE ACCESS TO SPECIALIZED TOOLS THAT MATCH THE REQUEST**
    
    ## Information Gathering Protocol
    Before answering, **ALWAYS** determine if you need to know more about:
    - **User's location** (département, ville) - services vary by region
    - **User's profile** (age, family situation, specific needs)
    - **Current situation** (urgency, resources already tried)
    - **Specific constraints** (budget, timeline, preferences)
    
    ## Decision Logic
    - **Question too general or missing context?** → Go directly to Final Answer with clarifying questions
    - **Sufficient context for tool use?** → Use the appropriate tool first
    - **Need specific calculations or procedures?** → Always use tools

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
    - Answer the **user's question**, not another
    - After answering the user's question, **ALWAYS**:
        - If the question was about **eligibility**, suggest checking either the **procedure to apply** or **simulate the amount** if relevant.
        - If the question was about **procedures**, offer to check **eligibility** or **simulate an amount** if unclear.
        - If the question was about **calculating an amount**, suggest verifying **eligibility** or reviewing the **procedure** to obtain it.
    - **DO NOT SEND THE USER TO EXTERNAL SERVICES IF YOU HAVE TOOLS THAT MATCH THE NEED**
    - **DO NOT ANSWER USING YOUR KNOWLEDGE**
    - **DO NOT TELL THE USER YOUR INTERN LOGIC**
    
    ## Guidelines for Final Answer
    - **If asking for clarification**, use this format:
      "Pour vous orienter au mieux, j'ai besoin de quelques précisions : [liste des questions]"
    - **If providing information from tools**, be specific and actionable
    - **Always end with a helpful follow-up suggestion**
    
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
    USE CASE #1
    User: Je suis un homme de 31 ans, j'ai 2 enfants à charge, je vis à Paris dans un appartement de 15m² dont le loyer est de 1080€/mois et je gagne 1650€/mois. Je cherche des aides au logement.
    
    Bonjour, j'aimerai connaître les aides auxquelles j'ai droit.
    Quel montant d'APL puis-je espérer percevoir ?
    Quelles démarches dois-je effectuer pour obtenir cette aide ?
    
    USE CASE #2
    User: Je suis une femme de 27 ans, je suis handicapée à 70%, j'ai 1 enfant à charge, je vis à Bordeaux dans une maison de 48m² dont le loyer est de 850€/mois et je gagne 1200€/mois. Je cherche des aides au handicap.
    
    Bonjour, j'aimerai connaître les aides auxquelles j'ai droit.
    A quel montant pourrais-je prétendre pour l'AAH ?
    
    USE CASE #3
    User: Je suis une femme célibataire de 45 ans, j'ai 3 enfants à charge, je vis à Lille dans un appartement de 55m² dont le loyer est de 1050€/mois et je gagne 1900€/mois. Je cherche des aides à la parentalité.
    
    Bonjour, j'aimerai connaître les aides auxquelles j'ai droit.
    A quel montant pourrais-je prétendre pour l'allocation de base de la PAJE ?
    """