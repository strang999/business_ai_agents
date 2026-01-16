from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool
import os

search_tool = SerperDevTool()

os.environ["OPENAI_MODEL_NAME"] = "gpt-4o-mini"

def create_newsletter_crew(topic):
    researcher = Agent(
        role='Research Analyst',
        goal=f'Find the latest and most relevant news about {topic}',
        backstory=f"You're an AI with a knack for discovering trending topics in {topic}.",
        tools=[search_tool]
    )

    writer = Agent(
        role='Content Writer',
        goal=f'Create engaging newsletter content about {topic} based on research',
        backstory=f"You're an AI with a talent for crafting compelling narratives about {topic}."
    )

    editor = Agent(
        role='Copy Editor',
        goal=f'Ensure the {topic} newsletter is polished and error-free',
        backstory="You're an AI with an eye for detail and a mastery of language."
    )

    research_task = Task(
        description=f'Find the top 3 trending topics in {topic} and provide brief summaries',
        agent=researcher,
        expected_output=f"A list of 3 trending {topic} topics with brief summaries for each"
    )

    writing_task = Task(
        description=f'Write a 300-word article on each trending {topic}',
        agent=writer,
        expected_output=f"Three 300-word articles about the trending {topic} topics"
    )

    editing_task = Task(
        description=f'Proofread and polish the {topic} articles, ensuring they flow well together',
        agent=editor,
        expected_output=f"A final, polished newsletter about {topic} trends, ready for distribution"
    )

    newsletter_crew = Crew(
        agents=[researcher, writer, editor],
        tasks=[research_task, writing_task, editing_task],
        verbose=True
    )

    return newsletter_crew

def main():
    topic = input("Enter the topic for the newsletter: ")
    crew = create_newsletter_crew(topic)
    result = crew.kickoff()
    print(result)

if __name__ == "__main__":
    main()