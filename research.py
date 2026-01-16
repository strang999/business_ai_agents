from crewai import Agent, Task, Crew, Process
from langchain_openai import OpenAI
from crewai_tools import SerperDevTool
import os

# Set up tools
search_tool = SerperDevTool()

# Set up language model
llm = OpenAI(model_name="gpt-4o-mini")

os.environ["OPENAI_MODEL_NAME"]="gpt-4o-mini"

# Create researcher agent
researcher = Agent(
    role="Senior Research Analyst",
    goal="Uncover cutting-edge developments in AI",
    backstory="You are an experienced research analyst with a keen eye for emerging trends in technology. Your expertise lies in identifying groundbreaking AI innovations and their potential impact on various industries.",
    verbose=True,
    allow_delegation=False,
    tools=[search_tool],
)

# Create writer agent
writer = Agent(
    role="Content Writer",
    goal="Create engaging articles about AI developments",
    backstory="You are a skilled writer with a passion for explaining complex technological concepts in simple terms. Your articles captivate readers while conveying accurate information about AI advancements.",
    verbose=True,
    allow_delegation=False,
)

research_task = Task(
    description="Research the latest advancements in AI and summarize the top 3 breakthroughs",
    agent=researcher,
    expected_output="A bullet-point list of the top 3 AI breakthroughs with a brief explanation of each"
)

writing_task = Task(
    description="Write a blog post about the top 3 AI breakthroughs",
    agent=writer,
    expected_output="A 500-word blog post discussing the top 3 AI breakthroughs",
    context=[research_task]
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,
    verbose=True,
)

result = crew.kickoff()
print(result)

