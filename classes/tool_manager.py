from win32com.servers.PythonTools import Tools

from classes.eligibility_tool import EligibilityTool
from classes.settings import Settings


class ToolManager:

    _instance = None
    _tools = None

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
        eligibility_tool = EligibilityTool().initialize(settings, vectorstore_manager)
        tools.append(eligibility_tool)
        return tools

    @property
    def tools(self):
        if self._tools is None:
            raise RuntimeError("ToolManager not initialized. Call initialize() first.")
        return self._tools