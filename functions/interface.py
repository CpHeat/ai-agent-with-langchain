import streamlit as st

from functions.agent.get_executor import get_executor


def interface(model, tools):

    st.title("Chatbot Aides Gouvernementales")

    if "agent_executor" not in st.session_state:
        st.session_state.agent_executor = get_executor(model, tools)

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
                response = st.session_state.agent_executor.invoke({"input": prompt})
                st.markdown(response["output"])
                st.session_state.messages.append({"role": "assistant", "content": response["output"]})
        st.rerun()

    # Bouton pour réinitialiser la conversation
    if st.button("Réinitialiser la conversation"):
        st.session_state.messages = []
        if "agent_executor" in st.session_state:
            st.session_state.agent_executor.memory.clear()
        st.rerun()