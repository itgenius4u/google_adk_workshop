from google.adk.agents.llm_agent import Agent
from google.adk.tools.tool_context import ToolContext

def set_preference(category: str, value: str, tool_context: ToolContext) -> dict:
    preferences = tool_context.state.get("user:preferences", {})
    preferences[category] = value
    tool_context.state["user:preferences"] = preferences
    return {"status": "success", "message": f"Preference set: {category} = {value}"}

def get_preferences(tool_context: ToolContext) -> dict:
    preferences = tool_context.state.get("user:preferences", {})
    return {"status": "success", "preferences": preferences}

root_agent = Agent(
    model='gemini-2.0-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    tools=[set_preference, get_preferences]
)
