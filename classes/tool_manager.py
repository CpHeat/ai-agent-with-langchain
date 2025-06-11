from classes.rag_tool import RagTool
from classes.settings import Settings


class ToolManager:

    _instance = None
    _tools:list = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, settings:Settings, vectorstore_manager):
        if self._tools is None:
            self._tools = self._create_tools(settings, vectorstore_manager)
        return self

    def _create_tools(self, settings, vectorstore_manager):
        tools = []

        eligibility_subtheme_filter = {"subtheme": {"$in": ["conditions"]}}
        eligibility_tool_prompt = "Tu es un assistant qui aide à trouver des informations concernant les droits disponibles en utilisant uniquement les documents qui te sont fournis."
        eligibility_tool_name = "Eligibility tool"
        eligibility_tool_description = "Gives you answers about eligibility to French government aids and social rights. Gives reliable answers based on documents."
        eligibility_tool = RagTool(settings, vectorstore_manager, eligibility_tool_prompt, eligibility_subtheme_filter, eligibility_tool_name, eligibility_tool_description).rag_tool

        procedure_subtheme_filter = {"subtheme": {"$in": ["démarches"]}}
        procedure_tool_prompt = "Tu es un assistant qui aide à trouver des informations concernant les démarches à effectuer pour accéder à des droits en utilisant uniquement les documents qui te sont fournis."
        procedure_tool_name = "Procedure tool"
        procedure_tool_description = "Gives you answers about procedures to obtain to French government aids and social rights. Gives reliable answers based on documents."
        procedure_tool = RagTool(settings, vectorstore_manager, procedure_tool_prompt, procedure_subtheme_filter, procedure_tool_name, procedure_tool_description).rag_tool

        simulation_subtheme_filter = {"subtheme": {"$in": ["calcul"]}}
        simulation_tool_prompt = "Tu es un assistant qui effectue des simulations concernant les montants des aides de l'état en utilisant uniquement les documents qui te sont fournis."
        simulation_tool_name = "simulation tool"
        simulation_tool_description = "Simulate a government assistance calculation to obtain an amount based on your personal situation. Gives reliable answers based on documents."
        simulation_tool = RagTool(settings, vectorstore_manager, simulation_tool_prompt, simulation_subtheme_filter, simulation_tool_name, simulation_tool_description).rag_tool

        tools.extend([eligibility_tool, procedure_tool, simulation_tool])
        return tools

    @property
    def tools(self):
        if self._tools is None:
            raise RuntimeError("ToolManager not initialized. Call initialize() first.")
        return self._tools