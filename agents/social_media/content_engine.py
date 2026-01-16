import os
import time
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI

load_dotenv()

# Initialize Tools
search_tool = SerperDevTool()

class ContentEngine:
    def __init__(self, topic: str):
        self.topic = topic
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    def create_agents(self):
        # 1. Trend Researcher
        researcher = Agent(
            role="Trend Researcher",
            goal=f"Find the latest trending discussions and news about {self.topic}",
            backstory="You are a viral content researcher who knows exactly what people are talking about right now.",
            verbose=True,
            allow_delegation=False,
            tools=[search_tool],
            llm=self.llm
        )

        # 2. Content Strategist
        strategist = Agent(
            role="Content Strategist",
            goal="Develop 3 unique content angles based on research",
            backstory="You are a master storyteller. You know how to take boring facts and turn them into hooks.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

        # 3. LinkedIn Ghostwriter
        writer = Agent(
            role="LinkedIn Ghostwriter",
            goal="Write 3 high-engagement LinkedIn posts",
            backstory="You are a top-tier LinkedIn creator. You use short sentences, strong hooks, and clear value props. No corporate jargon.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

        return [researcher, strategist, writer]

    def create_tasks(self, agents):
        researcher, strategist, writer = agents

        # Task 1: Research
        task1 = Task(
            description=f"Search for the top 3 trending news items, debates, or questions regarding '{self.topic}' from the last week.",
            agent=researcher,
            expected_output="A bulleted list of 3 key trends/news items with source links."
        )

        # Task 2: Strategy
        task2 = Task(
            description=f"Based on the research, propose 3 distinct angles for LinkedIn posts:\n1. Educational (How-to)\n2. Contrarian (Why X is wrong)\n3. Insight/News (Did you hear about Y?)",
            agent=strategist,
            expected_output="A plan outlining the 3 specific post ideas/angles."
        )

        # Task 3: Writing
        task3 = Task(
            description=f"Write 3 complete LinkedIn posts based on the approved angles. \nRequirements:\n- Use emojis sparingly.\n- One line per paragraph for readability.\n- Strong hook for each.\n- Call to action at the end.",
            agent=writer,
            expected_output="Three fully written LinkedIn posts formatted for copy-pasting."
        )

        return [task1, task2, task3]

    def run(self):
        agents = self.create_agents()
        tasks = self.create_tasks(agents)
        
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=True,
            process=Process.sequential
        )
        
        result = crew.kickoff()
        return result

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 CONTENT PIPELINE ENGINE")
    print("="*50)
    
    topic = input("Enter a topic to generate content for (e.g., 'AI Agents', 'Real Estate Market'): ")
    if not topic:
        topic = "AI Agents"
        
    engine = ContentEngine(topic)
    result = engine.run()
    
    print("\n" + "="*50)
    print("📝 FINAL GENERATED CONTENT")
    print("="*50)
    print(result)
    
    # Save to file
    filename = f"content_{int(time.time())}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(result))
    print(f"\n✅ Content saved to {filename}")
