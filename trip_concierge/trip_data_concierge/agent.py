# Borrowed from: https://colab.research.google.com/drive/1zzTZ8t6aYFbsyrWpGAtmirNdA9R-bbWz#scrollTo=LHAKKcmvgQKs

import asyncio
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

# Additional tooling
# --- ADK, Agent, and Evaluation Components ---
from google.adk.agents import Agent
from google.adk.events import Event
from google.adk.runners import Runner
import google.adk as adk
from google.adk.tools import google_search
from google.adk.sessions import InMemorySessionService, Session
from google.genai import types
from google.genai.types import Content, Part

# Assume 'db_agent' is a pre-defined NL2SQL Agent
# For this example, we'll create placeholder agents.

db_agent = Agent(
    name="db_agent",
    model="gemini-3.5-flash",
    instruction="You are a database agent. When asked for data, return this mock JSON object: {'status': 'success', 'data': [{'name': 'The Grand Hotel', 'rating': 5, 'reviews': 450}, {'name': 'Seaside Inn', 'rating': 4, 'reviews': 620}]}")

# --- 1. Define the Specialist Agents ---

# The Food Critic remains the deepest specialist
food_critic_agent = Agent(
    name="food_critic_agent",
    model="gemini-3.5-flash",
    instruction="You are a snobby but brilliant food critic. You ONLY respond with a single, witty restaurant suggestion near the provided location.",
)

# The Concierge knows how to use the Food Critic
concierge_agent = Agent(
    name="concierge_agent",
    model="gemini-3.5-flash",
    instruction="You are a five-star hotel concierge. If the user asks for a restaurant recommendation, you MUST use the `food_critic_agent` tool. Present the opinion to the user politely.",
    tools=[AgentTool(agent=food_critic_agent)]
)


# --- 2. Define the Tools for the Orchestrator ---

async def call_db_agent(
    question: str,
    tool_context: ToolContext,
):
    """
    Use this tool FIRST to connect to the database and retrieve a list of places, like hotels or landmarks.
    """
    print("--- TOOL CALL: call_db_agent ---")
    agent_tool = AgentTool(agent=db_agent)
    db_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    # Store the retrieved data in the context's state
    tool_context.state["retrieved_data"] = db_agent_output
    return db_agent_output


async def call_concierge_agent(
    question: str,
    tool_context: ToolContext,
):
    """
    After getting data with call_db_agent, use this tool to get travel advice, opinions, or recommendations.
    """
    print("--- TOOL CALL: call_concierge_agent ---")
    # Retrieve the data fetched by the previous tool
    input_data = tool_context.state.get("retrieved_data", "No data found.")

    # Formulate a new prompt for the concierge, giving it the data context
    question_with_data = f"""
    Context: The database returned the following data: {input_data}

    User's Request: {question}
    """

    agent_tool = AgentTool(agent=concierge_agent)
    concierge_output = await agent_tool.run_async(
        args={"request": question_with_data}, tool_context=tool_context
    )
    return concierge_output


# --- 3. Define the Top-Level Orchestrator Agent ---
# This is set as the root_agent so that commands like `adk run` will
# pick up on it correctly
root_agent = Agent(
    name="trip_data_concierge",
    model="gemini-3.5-flash",
    description="Top-level agent that queries a database for travel data, then calls a concierge agent for recommendations.",
    tools=[call_db_agent, call_concierge_agent],
    instruction="""
    You are a master travel planner who uses data to make recommendations.

    1.  **ALWAYS start with the `call_db_agent` tool** to fetch a list of places (like hotels) that match the user's criteria.

    2.  After you have the data, **use the `call_concierge_agent` tool** to answer any follow-up questions for recommendations, opinions, or advice related to the data you just found.
    """,
)

