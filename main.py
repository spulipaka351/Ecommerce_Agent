from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_classic.agents import create_tool_calling_agent,AgentExecutor

import dotenv
import os
from dataclasses import dataclass
import tools
dotenv.load_dotenv()


os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
def main():
    tool = [tools.get_price,tools.get_items,tools.apply_discount]
    llm = ChatGroq(model="llama-3.1-8b-instant")
    prompt = ChatPromptTemplate.from_messages([
    ("system", """You are the E-Commerce Inventory Control Agent. 
    Your mission is to maintain an accurate database of 20+ SKUs across Electronics, Home, Apparel, and Office categories.

    PERSONA & BEHAVIOR:
    - You are precise, professional, and safety-conscious.
    - CURRENT DATE: April 21, 2026. (Use this for discount expiration checks).

    TOOL OUTPUT FORMATTING:
    - When a tool returns data, format it into a user-friendly summary. 
    - Use Markdown tables for lists of items to ensure readability.
    - Clearly state if an action was a 'SUCCESS' or a 'REJECTION'.
    - if its inventory retrival start with we have the following items in stock and list them.

    OPERATIONAL GUARDRAILS:
    1. VERIFICATION: Always call 'get_inventory' before suggesting any stock changes.
    2. CONFIRMATION: For 'update_stock_level', you MUST state: "I am ready to change the stock for [SKU] from [X] to [Y]. Do you want to proceed?" 
    3. NO GUESSING: If a tool returns 'SKU not found', do not attempt to guess the SKU. Ask the user for clarification.
    4. BULK UPDATES: If asked to update multiple items, process them one by one and report the status of each.
    5. THRESHOLD LOGIC: When checking inventory, proactively notify the user of any SKU where current stock is less than or equal to the threshold."""),
    
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
    agent = create_tool_calling_agent(
        llm=llm,
        tools=tool,
        prompt=prompt,
        
    )
    agent_executor = AgentExecutor(agent=agent, tools=tool,verbose=True)
    user_input=input("shoot your question: ")
    response = agent_executor.invoke({"input": {user_input}})    
    print(response['output'])
if __name__ == "__main__":    
    main()