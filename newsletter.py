from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool
import os

search_tool = SerperDevTool()

os.environ["OPENAI_MODEL_NAME"]="o1-mini"

researcher = Agent(
    role='Research Analyst',
    goal='Find the latest and most relevant tech news',
    backstory="You're an research analyst with a knack for discovering trending topics in tech.",
    tools=[search_tool]
)

writer = Agent(
    role='Content Writer',
    goal='Create engaging newsletter content based on research',
    backstory="You're a content writer with a talent for crafting compelling narratives."
)

editor = Agent(
    role='Copy Editor',
    goal='Ensure the newsletter is polished, error-free, and well-integrated',
    backstory="You're a editor with an eye for detail, a mastery of language, and the ability to seamlessly integrate personalized content."
)

personalizer = Agent(
    role='Content Personalizer',
    goal='Craft personalized introductions for different reader segments',
    backstory="You're an content personalizer expert in analyzing reader preferences and creating engaging, personalized content.",
    tools=[search_tool]

)

research_task = Task(
    description='Find the top 3 trending topics in AI and provide brief summaries',
    agent=researcher,
    expected_output=f"A list of 3 trending topics with brief summaries for each"
)

writing_task = Task(
    description='Write a 300-word article on each trending topic',
    agent=writer,
    expected_output=f"Three 300-word articles about the trending topics"
)

editing_task = Task(
    description='Proofread and polish the articles, ensuring they flow well together. Integrate the personalized introduction seamlessly.',
    agent=editor,
    expected_output="Ensure newsletter is polished."
)

personalization_task = Task(
    description='Analyze reader data and create a personalized introduction for the newsletter',
    agent=personalizer,
    expected_output = 'Summary of a personalised intro'
)

newsletter_crew = Crew(
    agents=[researcher, writer, editor, personalizer],
    tasks=[research_task, writing_task, editing_task, personalization_task],
    verbose=True
)

result = newsletter_crew.kickoff()
print(result)

