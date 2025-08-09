from google.adk.agents.llm_agent import Agent
from google.adk.agents.sequential_agent import SequentialAgent

code_writer_agent = Agent(
    model='gemini-2.0-flash',
    name='code_writer_agent',
    description='You are a Code Writer AI.',
    instruction="""You are a Code Writer AI.Based on the user's \
        request, write the initial Python code."""
)
code_reviewer_agent = Agent(
    model='gemini-2.0-flash',
    name='code_reviewer_agent',
    description='You are a Code Reviewer AI.',
    instruction='Review the Python code provided in the session state',
)
root_agent = SequentialAgent(
    name="CodePipelineAgent",
    sub_agents=[code_writer_agent, code_reviewer_agent],
)