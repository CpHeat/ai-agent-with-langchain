import os

from IPython.display import display, clear_output, Markdown
from dotenv import load_dotenv
from datetime import datetime
from langchain_ollama import ChatOllama
from langchain_deepseek import ChatDeepSeek
from langchain import hub
from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from pprint import pprint


def initialize_agent(model, tools):

    prompt = hub.pull("hwchase17/react-chat")

    memory= ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    #creation agent
    agent=create_react_agent(
        llm=model,
        tools=tools,
        prompt=prompt,
        stop_sequence=True    
    )

    #encapsulation agent
    #enlever dans la version final mettre Verbose a false
    executor=AgentExecutor.from_agent_and_tools( 
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True
    )