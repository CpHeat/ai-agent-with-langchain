import streamlit as st

from functions.agent.get_executor import get_executor
from settings import params


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

                if params['debug']:
                    debug_message = "### Debug\n"
                    debug_message += f"Agent query to the tool: {params['debug_query']}\n\n"

                    if len(params['debug_log']) == 0:
                        debug_message += "No documents were used for this answer\n"
                    else:
                        debug_message += f"{len(params['debug_log'])} document(s) were used for this answer:\n\n"
                        for debug_dict in params['debug_log']:
                            debug_message += (
                                f"- Source: {debug_dict['document_source']}\n"
                                f"- Themes: {debug_dict['document_large_theme']} \\ {debug_dict['document_theme']}\n"
                                f"- Content: {debug_dict['document_content']}\n\n"
                            )

                st.session_state.messages.append({"role": "assistant", "content": debug_message})
        st.rerun()

    # Bouton pour réinitialiser la conversation
    if st.button("Réinitialiser la conversation"):
        st.session_state.messages = []
        if "agent_executor" in st.session_state:
            st.session_state.agent_executor.memory.clear()
        st.rerun()