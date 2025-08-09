from google.adk.agents.llm_agent import Agent

help_agent = Agent(
    model='gemini-2.5-flash', # gemini-2.0-flash-live-001
    # model='gemini-2.0-flash-live-001',
    name='help_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)
root_agent = help_agent
