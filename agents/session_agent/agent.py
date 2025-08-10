from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.0-flash',
    name='root_agent',
    description="An agent that knows some things about the user and their posts preferences",
    instruction="""
        You are a helpful assistant that can respond about the user and their post preferences.

    The information about the user and their post preferences is given in the state context.
    Name: {user_name}
    Post Preferences: {user_post_preferences}
    """,
)
