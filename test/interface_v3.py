import sys
import os
from pathlib import Path

# Ajouter le dossier parent (racine du projet) au Python path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime

import streamlit as st

from classes.settings import Settings
from classes.agent_manager import AgentManager
from classes.interface_manager import InterfaceManager
from classes.vectorstore_manager import VectorstoreManager
from classes.tool_manager import ToolManager


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
    
    def _create_interface(self, settings:Settings, agent_manager):
        st.set_page_config(
            page_title="Chatbot Aides Gouvernementales",
            page_icon="🇫🇷",
            layout="centered",
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

            .sidebar-info {
                background: #f1f3f4;
                padding: 1rem;
                border-radius: 10px;
                text-align: center;
                color: #666;
                margin-top: 2rem;
                font-size: 0.9rem;
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
                    
        # Header :
        st.markdown("""
                    <div class="main-header">
                        <h1>ADA : Aide aux Droits Assistant</h1>
                        <p>Votre assistant personnel pour les aides sociales, financières et administratives</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Section d'exemples de prompt :
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
        
        # Initialisation de l'agent :
        if "agent_executor" not in st.session_state:
            st.session_state.agent_executor = agent_manager.executor
            
        # Initialisation de l'historique des messages :
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        # Initialisation de l'historique du chat :
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
        # Afficher les messages existants :
        if st.session_state.messages:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for message in st.session_state.messages:
                role = message.get("role", "user")
                content = message.get("content", "")
                with st.chat_message(role, avatar="🤖" if role == "assistant" else "👤"):
                    st.markdown(content)
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Saisie utilisateur :
        if prompt := st.chat_input("Posez votre question sur les aides gouvernementales..."):
            
            # Enregistre et affiche la question de l'utilisateur :
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
            
            # Génère et affiche la réponse :
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("🔍 Recherche des informations..."):
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
                        debug_message += f"Agent query to the toll : {settings.params['debug_query']}\n\n"
                        
                        if len(settings.params['debug_log']) == 0:
                            debug_message += "No documents were used for this answer\n"
                        else :
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
            
        # Sidebar :
        
        with st.sidebar:
            
            # Liens utiles :
            st.markdown("### 🔗 Liens utiles")
            st.markdown("""
            - [Service-public.fr](https://www.service-public.fr)
            - [CAF](https://www.caf.fr)
             - [Pôle Emploi](https://www.pole-emploi.fr)
             - [Mes Aides](https://mes-aides.gouv.fr)
            """)
            
            # Statistiques de la page :
            st.markdown("### 📊 Statistiques")
            st.metric("Messages échangés", len(st.session_state.messages))
            
            # Informations supplémentaires :
            st.markdown("### ℹ️ Informations supplémentaires")
            st.markdown("""
                <div class="footer-info">
                    Ce chatbot est conçu pour vous orienter vers les aides disponibles. 
                    Pour des démarches officielles, consultez toujours les sites gouvernementaux officiels 
                    ou contactez les services compétents.
                </div>
                """, unsafe_allow_html=True)
            
            # Bouton de réinitialisation de la conversation :
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Réinitialiser la conversation"):
                st.session_state.messages = []
                if "agent_executor" in st.session_state:
                    st.session_state.agent_executor.memory.clear()
                st.experimental_rerun()
                
    @property
    def interface(self):
        if self._interface is None:
            raise RuntimeError("Interface not initialized. Call initialize() first.")
        return self._interface
    
if __name__ == "__main__":

    settings = Settings()
    vectorstore_manager = VectorstoreManager().initialize(settings)
    tools = ToolManager().initialize(settings, vectorstore_manager).tools
    agent_manager = AgentManager().initialize(settings, tools)
    interface_manager = InterfaceManager().initialize(settings, agent_manager)
