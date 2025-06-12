from datetime import datetime

import streamlit as st

from classes.settings import Settings


class InterfaceManager:

    _instance = None
    _interface = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, settings: Settings, agent_manager):
        if self._interface is None:
            self._interface = self._create_interface(settings, agent_manager)
        return self._interface

    def _create_interface(self, settings, agent_manager):
        st.set_page_config(
            page_title="Chatbot Aides Gouvernementales",
            page_icon="🇫🇷",
            layout="centered",
            initial_sidebar_state="collapsed"
        )

        st.markdown("""
            <div class="main-header">
                <h1>Chatbot Aides Gouvernementales</h1>
                <p>Votre assistant personnel pour les aides sociales, financières et administratives</p>
            </div>
            """, unsafe_allow_html=True)

        if "agent_executor" not in st.session_state:
            st.session_state.agent_executor = agent_manager

        # Initialiser l'historique des messages
        if "messages" not in st.session_state:
            st.session_state.messages = []

        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

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

                    st.session_state.chat_history.append({
                        "user": prompt,
                        "assistant": response["output"],
                        "timestamp": datetime.now()
                    })

                    st.markdown(response["output"])

                    st.session_state.messages.append({"role": "assistant", "content": response["output"]})

                    if settings.params['debug']:
                        debug_message = "### Debug\n"
                        debug_message += f"Agent query to the tool: {settings.params['debug_query']}\n\n"

                        if len(settings.params['debug_log']) == 0:
                            debug_message += "No documents were used for this answer\n"
                        else:
                            debug_message += f"{len(settings.params['debug_log'])} document(s) were used for this answer:\n"
                            for debug_dict in settings.params['debug_log']:
                                debug_message += (
                                    f"- Source: {debug_dict['document_source']}\n"
                                    f"- Themes: {debug_dict['document_large_theme']} \\ {debug_dict['document_theme']}\n"
                                    # f"- Content: {debug_dict['document_content']}\n\n"
                                )
                        settings.params['debug_log'] = []

                    st.session_state.messages.append({"role": "assistant", "content": debug_message, "type": "debug"})
            st.rerun()

        # 📋 Informations supplémentaires
        st.markdown("""
            <div class="footer-info">
                <strong>ℹ️ Informations importantes :</strong><br>
                Ce chatbot est conçu pour vous orienter vers les aides disponibles. 
                Pour des démarches officielles, consultez toujours les sites gouvernementaux officiels 
                ou contactez les services compétents.
            </div>
            """, unsafe_allow_html=True)

        # Bouton pour réinitialiser la conversation
        if st.button("Réinitialiser la conversation"):
            st.session_state.messages = []
            if "agent_executor" in st.session_state:
                st.session_state.agent_executor.memory.clear()
            st.rerun()

    @property
    def interface(self):
        if self._interface is None:
            raise RuntimeError("Interface not initialized. Call initialize() first.")
        return self._interface