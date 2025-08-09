from google.adk.agents.llm_agent import Agent

def get_capital_city(country: str) -> str:
    """Retrieves the capital city for a given country."""
    capitals = {"korea": "Seoul", "canada": "Ottawa"}
    return capitals.get(country.lower(), f"Sorry, I don't know the capital of {country}.")

root_agent = Agent(
    model='gemini-2.0-flash',
    name='capital_agent',
    description="Answers user questions about the capital city of a given country.",
    instruction="""You are an agent that provides the capital city of a country... (previous instruction text)""",
    tools=[get_capital_city]
)
