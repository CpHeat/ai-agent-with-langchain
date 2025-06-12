from classes.rag_tool import RagTool
from classes.settings import Settings


class ToolManager:

    _instance = None
    _tools:list = None
    _settings:Settings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, settings:Settings, vectorstore_manager):
        self._settings = settings
        if self._tools is None:
            self._tools = self._create_tools(vectorstore_manager)
        return self

    def _create_tools(self, vectorstore_manager):
        tools = []

        for tool in self._settings.tools:
            rag_tool = RagTool(self._settings, vectorstore_manager, tool['prompt'], tool['filter'], tool['name'], tool['description']).rag_tool
            tools.append(rag_tool)

        return tools

    @property
    def tools(self):
        if self._tools is None:
            raise RuntimeError("ToolManager not initialized. Call initialize() first.")
        return self._tools