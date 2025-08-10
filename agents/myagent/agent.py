from google.adk.agents.llm_agent import Agent
from google.adk.agents import SequentialAgent

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (41 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }

step1 = Agent(name="data_collector", model='gemini-2.0-flash',
              instruction="You're a data collector.")
step2 = Agent(name="data_analyzer", model='gemini-2.0-flash',
              instruction="You're a data analyzer.")

pipeline = SequentialAgent(name="analysis_pipeline", 
    sub_agents=[step1, step2]
)
root_agent = pipeline

help_agent = Agent(
    model='gemini-2.0-flash',
    name='help_agent',
    description='Agent to answer questions about the time and weather in a city.',
    instruction='I can answer your questions about the time and weather in a city',
    # tools=[get_weather],
)
