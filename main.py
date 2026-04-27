from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_classic.agents import create_tool_calling_agent,AgentExecutor
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import  RunnableWithMessageHistory
import dotenv
import os
from typing import TypedDict, Annotated

import tools

dotenv.load_dotenv()


os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
def main():
    tool = [tools.get_price,tools.get_inventory,tools.apply_discount,tools.check_low_stock,tools.update_stock_level,tools.flag_items,tools.validate_discount_code]
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    prompt = ChatPromptTemplate.from_messages([
    ("system", """You are the E-Commerce Inventory Control Agent. 
    Your mission is to maintain an accurate database of 20+ SKUs across Electronics, Home, Apparel, and Office categories.

    PERSONA & BEHAVIOR:
    - You are precise, professional, and safety-conscious.
    - CURRENT DATE: April 21, 2026. (Use this for discount expiration checks).

    TOOL OUTPUT FORMATTING:
    - When a tool returns data, format it into a user-friendly summary.
    - Do not return raw tool outputs directly to the user. Always interpret and summarize the results. 
    - Clearly state if an action was a 'SUCCESS' or a 'REJECTION'.
    - if its inventory retrival start with we have the following items in stock and list them.

    OPERATIONAL GUARDRAILS:
    1. VERIFICATION: Only call 'get_inventory' if the user requests a list of available items else do not call it.
    2. CONFIRMATION: For 'update_stock_level', you MUST state: "I am ready to change the stock for [SKU] from [X] to [Y]. Do you want to proceed?" 
    3. NO GUESSING: If a tool returns 'SKU not found', do not attempt to guess the SKU. Ask the user for clarification.
    4. BULK UPDATES: If asked to update multiple items, process them one by one and report the status of each.
    5. Update the stock levels of items when the user requests it. Always confirm the change with the user before applying it.
    6. THRESHOLD LOGIC: When checking inventory, proactively notify the user of any SKU where current stock is less than or equal to the threshold."""),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
    

])
    agent = create_tool_calling_agent(
        llm=llm,
        tools=tool,
        prompt=prompt,
        
        
    )

    agent_executor = AgentExecutor(agent=agent, tools=tool, verbose=True)

    store = {}
    def get_session_history(session_id: str) -> ChatMessageHistory:
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]

    agent_with_history = RunnableWithMessageHistory(
        agent_executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    while True:
        user_input=input("shoot your question: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the E-Commerce Inventory Control Agent. Goodbye!")
            break
        response = agent_with_history.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": "session1"}}
        )    
        print(response['output'])
if __name__ == "__main__":    
    main()