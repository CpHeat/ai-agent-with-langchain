import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_deepseek import ChatDeepSeek
from langchain import hub
from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from IPython.display import display, clear_output, Markdown

load_dotenv(override=True)

# model = ChatOllama(model="llama3", temperature=0)
model = ChatDeepSeek(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY"))

def data_right_disability(query):
    return "Voici les droits sur les handicapées"

def data_right_child(query):
    return "Voici les droits sur les enfants"

def data_right_accommodation(query):
    return "Voici les droits sur les logements"

def error_handle_message(query):
    return "Je n'ai pas compris la requête veuillez reformuler votre message"

tools = [
    Tool(name="right_disability", func=data_right_disability, description="Droits handicap"),
    Tool(name="right_child", func=data_right_child, description="Droits enfants"),
    Tool(name="right_accommodation", func=data_right_accommodation, description="Droits logement"),
    Tool(name="generate_message", func=error_handle_message, description="Message erreur")
]

prompt = hub.pull("hwchase17/react-chat")
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = create_react_agent(
    llm=model,
    tools=tools,
    prompt=prompt,
    stop_sequence=True
)

executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True
)

if __name__ == "__main__":
    while True:
        user_input = input("Vous : ")
        clear_output(wait=True)
        display(Markdown(f"**Vous :** {user_input}"))

        if user_input.lower() in ["stop", "exit", "quit"]:
            print("Fin de la conversation.")
            break

        response = executor.invoke({"input": user_input})
        display(Markdown(response["output"]))
