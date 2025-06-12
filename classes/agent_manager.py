from langchain.agents import create_react_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate

from classes.settings import Settings


class AgentManager:

    _instance = None
    _executor = None
    _settings:Settings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, settings, tools):
        self._settings = settings
        if self._executor is None:
            self._executor = self._create_executor(tools)
        return self

    def _create_executor(self, tools):
        prompt = self._get_prompt()

        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # agent creation
        agent = create_react_agent(
            llm=self._settings.agent_model,
            tools=tools,
            prompt=prompt,
            stop_sequence=True
        )

        # agent encapsulation
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=self._settings.params['debug'],
            max_iterations=10,
            handle_parsing_errors=True
        )

        return agent_executor

    def _get_prompt(self):
        return PromptTemplate.from_template(self._settings.agent_prompt_template)

    @property
    def executor(self):
        if self._executor is None:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        return self._executor