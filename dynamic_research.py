from crewai import Agent, Task, Crew, Process
from langchain_openai import OpenAI
from crewai_tools import SerperDevTool
import os

# Set up tools
search_tool = SerperDevTool()

# Set up language model
llm = OpenAI(model_name="gpt-4o-mini")

os.environ["OPENAI_MODEL_NAME"] = "gpt-4o-mini"

def create_crew(topic):
    # Create researcher agent
    researcher = Agent(
        role="Senior Research Analyst",
        goal=f"Uncover cutting-edge developments in {topic}",
        backstory=f"You are an experienced research analyst with a keen eye for emerging trends in {topic}. Your expertise lies in identifying groundbreaking innovations and their potential impact on various industries.",
        verbose=True,
        allow_delegation=False,
        tools=[search_tool],
    )

    # Create writer agent
    writer = Agent(
        role="Content Writer",
        goal=f"Create engaging articles about {topic} developments",
        backstory=f"You are a skilled writer with a passion for explaining complex {topic} concepts in simple terms. Your articles captivate readers while conveying accurate information about advancements in {topic}.",
        verbose=True,
        allow_delegation=False,
    )

    research_task = Task(
        description=f"Research the latest advancements in {topic} and summarize the top 3 breakthroughs",
        agent=researcher,
        expected_output=f"A bullet-point list of the top 3 {topic} breakthroughs with a brief explanation of each"
    )

    writing_task = Task(
        description=f"Write a blog post about the top 3 {topic} breakthroughs",
        agent=writer,
        expected_output=f"A 500-word blog post discussing the top 3 {topic} breakthroughs",
        context=[research_task]
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        verbose=True,
    )

    return crew

def main():
    topic = input("Enter the topic you want to research: ")
    crew = create_crew(topic)
    result = crew.kickoff()
    print(result)

if __name__ == "__main__":
    main()