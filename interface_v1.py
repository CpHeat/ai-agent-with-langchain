import streamlit as st
from agent_rag import executor

def repondre_utilisateur(question):
    if not question.strip():
        return "Merci de poser une question claire sur une aide gouvernementale."
    try:
        chat_history = []
        messages = st.session_state.messages

        for i in range(0, len(messages) - 1, 2):
            if messages[i][0] == "user" and messages[i+1][0] == "assistant":
                chat_history.append((messages[i][1], messages[i+1][1]))

        response = executor.invoke({
            "input": question,
            "chat_history": chat_history
        })

        return response.get("output", "❌ Réponse invalide reçue du modèle.")
    except Exception as e:
        return f"❌ Une erreur est survenue : {e}"

st.set_page_config(
    page_title="Chatbot Aides Gouvernementales",
    page_icon="🇫🇷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 0;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
    }
    .examples-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        color: black;
    }
    .example-question {
        background: white;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
        font-style: italic;
        color: #555;
    }
    .chat-container {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    .footer-info {
        background: #f1f3f4;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: #666;
        margin-top: 2rem;
        font-size: 0.9rem;
    }
    .reset-button-container {
        display: flex;
        justify-content: center;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #e0e0e0;
    }
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        .main-header p {
            font-size: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>Chatbot des Aides Gouvernementales</h1>
    <p>Votre assistant personnel pour les aides sociales, financières et administratives</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="examples-container">
    <h3>💡 Exemple de prompt</h3>
    <div class="example-question">💰 "Ai-je droit à la prime d'activité ?"</div>
    <div class="example-question">🏠 "Puis-je bénéficier des APL ?"</div>
    <div class="example-question">👨‍👩‍👧 "Quelles aides pour une famille monoparentale ?"</div>
    <div class="example-question">🎓 "Existe-t-il des bourses d'études pour mon profil ?"</div>
    <div class="example-question">🚗 "Comment obtenir une aide pour l'achat d'un véhicule électrique ?"</div>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.session_state.messages:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for role, content in st.session_state.messages:
        with st.chat_message(role, avatar="🤖" if role == "assistant" else "👤"):
            st.markdown(content)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="footer-info">
    <strong>ℹ️ Informations importantes :</strong><br>
    Ce chatbot est conçu pour vous orienter vers les aides disponibles. 
    Pour des démarches officielles, consultez toujours les sites gouvernementaux officiels 
    ou contactez les services compétents.
</div>
""", unsafe_allow_html=True)

if prompt := st.chat_input("💬 Posez votre question sur les aides gouvernementales..."):
    st.session_state.messages.append(("user", prompt))
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🔍 Recherche des informations..."):
            response = repondre_utilisateur(prompt)
            st.markdown(response)
    st.session_state.messages.append(("assistant", response))
    st.rerun()

st.markdown('<div class="reset-button-container">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🗑️ Nouvelle conversation", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔗 Liens utiles")
    st.markdown("""
    - [Service-public.fr](https://www.service-public.fr)
    - [CAF](https://www.caf.fr)
    - [Pôle Emploi](https://www.pole-emploi.fr)
    - [Mes Aides](https://mes-aides.gouv.fr)
    """)

    st.markdown("### 📊 Statistiques")
    st.metric("Messages échangés", len(st.session_state.messages))

    st.markdown("### 🛠️ À propos")
    st.info("Version 1.0 - Interface améliorée pour une meilleure expérience utilisateur")
