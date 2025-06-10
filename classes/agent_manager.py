from langchain.agents import create_react_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate

from classes.settings import Settings


class AgentManager:

    _instance = None
    _executor = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, settings, tools):
        if self._executor is None:
            self._executor = self._create_executor(settings, tools)
        return self

    def _create_executor(self, settings:Settings, tools):
        prompt = self._get_prompt(settings)

        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # agent creation
        agent = create_react_agent(
            llm=settings.agent_model,
            tools=tools,
            prompt=prompt,
            stop_sequence=True
        )

        # agent encapsulation
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=False,
            max_iterations=5,
            early_stopping_method="generate",
            handle_parsing_errors=True
        )

        return agent_executor

    @classmethod
    def _get_prompt(cls, settings:Settings):
        return PromptTemplate.from_template(settings.agent_prompt_template)

    def _get_tools(cls, model, retriever):
        pass

    @property
    def executor(self):
        if self._executor is None:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        return self._executor