from win32com.servers.PythonTools import Tools

from classes.rag_tool import RagTool
from classes.settings import Settings


class ToolManager:

    _instance = None
    _tools = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, settings:Settings, retriever):
        if self._tools is None:
            self._tools = self._create_tools(settings, retriever)
        return self

    def _create_tools(self, settings, retriever):
        tools = []
        rag_tool = RagTool().initialize(settings, retriever)
        tools.append(rag_tool)
        return tools

    @property
    def tools(self):
        if self._tools is None:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        return self._tools