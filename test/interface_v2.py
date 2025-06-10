import streamlit as st
from langchain_ollama import ChatOllama

st.title("Chatbot Aides Gouvernementales")

# Initialiser ChatOllama avec le modèle local 'llama3'
client = ChatOllama(model="llama3.2")

# Initialiser le modèle dans la session
if "chat" not in st.session_state:
    st.session_state["chat"] = client

# Initialiser l'historique des messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher les messages existants
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Saisie utilisateur
if prompt := st.chat_input("Posez votre question sur les aides gouvernementales…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Réflexion en cours..."):
            response = client.invoke(prompt)
            st.markdown(response.content)
            st.session_state.messages.append({"role": "assistant", "content": response.content})
    st.rerun()
# Bouton pour réinitialiser la conversation
if st.button("Réinitialiser la conversation"):
    st.session_state.messages = []
    st.rerun()