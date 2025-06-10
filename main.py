from classes.agent_manager import AgentManager
from classes.interface_manager import InterfaceManager
from classes.settings import Settings
from classes.tool_manager import ToolManager
from classes.vectorstore_manager import VectorstoreManager


if __name__ == "__main__":

    settings = Settings()
    vectorstore_manager = VectorstoreManager().initialize(settings)
    tools = ToolManager().initialize(settings, vectorstore_manager.retriever).tools
    agent_executor = AgentManager().initialize(settings, tools).executor
    interface_manager = InterfaceManager().initialize(settings, agent_executor)