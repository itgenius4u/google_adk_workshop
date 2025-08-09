from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search

root_agent = Agent(
    model='gemini-2.0-flash',
    name='tool_agent',
    description='도구 에이전트',
    instruction='귀하는 다음 도구를 사용할 수 잇는 유용한 도우미입니다.',
    tools=[google_search],
)