from datetime import datetime

import streamlit as st
from streamlit_extras.stylable_container import stylable_container

from classes.settings import Settings


class InterfaceManager:

    _instance = None
    _interface = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, settings:Settings, agent_manager):
        if self._interface is None:
            self._interface = self._create_interface(settings, agent_manager)
        return self._interface

    def _create_interface(self, settings, agent_manager):

        self._header()
        self._sidebar(settings)

        if "agent_executor" not in st.session_state:
            st.session_state.agent_executor = agent_manager

        # Message history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        self._body(settings)
        self._css()

    def _css(self):
        st.markdown("""
            <style>
            .debug-message {
                background-color: #fff3cd;
                color: #856404;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #ffeeba;
                font-family: monospace;
                margin-bottom: 10px;
            }
            .stExpander {
                font-weight: bold;
                color: #856404;
                background-color: #fff3cd;
                padding: 8px;
                border-radius: 5px;
            }
        
            /* Contenu interne de l'expander */
            .stExpanderDetail {
                background-color: #fffbea;
                padding: 10px;
                border: 1px solid #ffeeba;
                border-radius: 5px;
            }
            </style>
        """, unsafe_allow_html=True)

    def _body(self, settings:Settings):
        # Show messages
        self._messages()
        # User input
        if prompt := st.chat_input("Posez votre question sur les aides gouvernementales…"):
            self._css()
            st.session_state.messages.append({"role": "user", "content": prompt, "type": "user"})
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

                    st.session_state.messages.append({"role": "assistant", "content": response["output"], "type": "ai"})

                    self._debug(settings)

            st.rerun()

    def _sidebar(self, settings:Settings):
        self._important_context()
        self._debug_checkbox(settings)
        self._reset_button()

    def _debug_checkbox(self, settings:Settings):
        # Affichage de la case à cocher
        debug_mode = st.sidebar.checkbox("Afficher debug", value=settings.params["debug"])

        # Mise à jour de settings.params['debug']
        settings.params["debug"] = debug_mode

    def _messages(self):
        for message in st.session_state.messages:
            if message["type"] == "debug":
                st.markdown(f'<div class="debug-message">{message["content"]}</div>', unsafe_allow_html=True)
            elif message["type"] == "debug-source":
                with st.expander(message["content"]):
                    st.markdown(f"```\n{message['extended-content']}\n```")
            else:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    def _header(self):
        st.set_page_config(
            page_title="Chatbot Aides Gouvernementales",
            page_icon="🇫🇷",
            layout="centered",
            initial_sidebar_state="expanded"
        )

        st.markdown("""
            <div class="main-header">
                <h1>Chatbot Aides Gouvernementales</h1>
                <p>Votre assistant personnel pour les aides sociales, financières et administratives</p>
            </div>
            """, unsafe_allow_html=True)

    def _debug(self, settings):
        if settings.params['debug']:

            debug_message = ""

            if settings.params['debug_used_tool'] is not None:
                debug_message += f"Agent used a tool: {settings.params['debug_used_tool']}\n\n"
                debug_message += f"Agent query to the tool: {settings.params['debug_query']}\n\n"
            else:
                debug_message += f"Agent used no tool\n\n"

            if settings.params['debug_used_tool'] is not None:
                debug_message += f"{len(settings.params['debug_log'])} document(s) used\n"

            st.session_state.messages.append({"role": "assistant", "content": debug_message, "type": "debug"})

            for debug_dict in settings.params['debug_log']:
                debug_message = (
                    f"Source: {debug_dict['document_source']} | Theme: {debug_dict['document_large_theme']} | Subtheme: {debug_dict['document_theme']}\n"
                )
                st.session_state.messages.append(
                    {"role": "assistant", "content": debug_message, "extended-content": debug_dict['document_content'], "type": "debug-source"})

            settings.params['debug_log'] = []
            settings.params['debug_query'] = None
            settings.params['debug_used_tool'] = None

    def _important_context(self):
        st.sidebar.markdown("""
            <div class="footer-info">
                <strong>ℹ️ Informations importantes :</strong><br>
                Ce chatbot est conçu pour vous orienter vers les aides disponibles. 
                Pour des démarches officielles, consultez toujours les sites gouvernementaux officiels 
                ou contactez les services compétents.
            </div>
            """, unsafe_allow_html=True)

    def _reset_button(self):
        if st.sidebar.button("Réinitialiser la conversation"):
            st.session_state.messages = []
            if "agent_executor" in st.session_state:
                st.session_state.agent_executor.memory.clear()
            st.rerun()

    @property
    def interface(self):
        if self._interface is None:
            raise RuntimeError("Interface not initialized. Call initialize() first.")
        return self._interface