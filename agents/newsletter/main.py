import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama

load_dotenv()
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

search_tool = SerperDevTool()

def get_llm(use_gpt=True):
    if use_gpt:
        return LLM(model="openai/gpt-4o-mini", temperature=0.7)
    return Ollama(
        model="deepseek-r1:latest",
        base_url="http://localhost:11434",
        temperature=0.7
    )

def create_agents(use_gpt=True):
    llm = get_llm(use_gpt)
    
    researcher = Agent(
        role='Research Specialist',
        goal='Find comprehensive and up-to-date information on topics',
        backstory='Expert researcher skilled at discovering reliable information from various sources',
        tools=[search_tool],
        llm=llm,
        verbose=True
    )
    
    fact_checker = Agent(
        role='Fact Verification Specialist',
        goal='Verify accuracy of information and cross-reference sources',
        backstory='Meticulous fact-checker with years of experience in verification and validation',
        tools=[search_tool],
        llm=llm,
        verbose=True
    )
    
    writer = Agent(
        role='Newsletter Writer',
        goal='Create engaging and well-structured newsletters',
        backstory='Professional writer specializing in creating compelling newsletters with clear structure and engaging content',
        llm=llm,
        verbose=True
    )
    
    return researcher, fact_checker, writer

def create_tasks(researcher, fact_checker, writer, topic):
    research_task = Task(
        description=f"Research the latest developments, key trends, and important insights about: {topic}",
        agent=researcher,
        expected_output="A detailed summary of the topic with key points and references"
    )
    
    verify_task = Task(
        description="Verify the accuracy of the research findings and identify any conflicting information",
        agent=fact_checker,
        context=[research_task],
        expected_output="A comprehensive report on the accuracy of the research findings and any conflicting information"
    )
    
    newsletter_task = Task(
        description=f"""Create a newsletter about {topic} with the following format:
        - Title
        - Subtitle
        - Topic overview
        - H1, H2, H3 headers for main points
        - 500-word blog post
        Make it engaging and well-structured.""",
        agent=writer,
        context=[research_task, verify_task],
        expected_output="A well-structured newsletter in HTML format"
    )
    
    return [research_task, verify_task, newsletter_task]

def create_crew(agents, tasks):
    return Crew(
        agents=agents,
        tasks=tasks,
        verbose=True
    )

def main():
    print("Welcome to the Newsletter Creation Crew!")
    use_gpt = input("Use GPT-4? (yes/no): ").lower() == 'yes'
    
    if not use_gpt:
        print("\nUsing Ollama - Ensure it's running on http://localhost:11434")
        print("Start with: ollama run deepseek-r1:latest")
    
    topic = input("\nNewsletter topic: ")
    
    try:
        researcher, fact_checker, writer = create_agents(use_gpt)
        tasks = create_tasks(researcher, fact_checker, writer, topic)
        crew = create_crew([researcher, fact_checker, writer], tasks)
        
        result = crew.kickoff()
        print("\nNewsletter Result:")
        print(result)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        if not use_gpt:
            print("\nTip: Ensure Ollama is running with the deepseek-r1:latest model")
            print("Run: ollama pull deepseek-r1:latest")

if __name__ == "__main__":
    main()