import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool, WebsiteSearchTool
import streamlit as st
from datetime import datetime
import pandas as pd
import json
import time

# Load environment variables
load_dotenv()
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY", "")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY", "")

# Initialize enhanced search tools
search_tool = SerperDevTool()
website_tool = WebsiteSearchTool()

def get_claude_llm():
    """Get the Claude 3.7 Sonnet language model"""
    return LLM(
        model="anthropic/claude-3-7-sonnet-20250219",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.7,
        verbose=True
    )

def create_content_calendar_agents():
    """Create specialized agents for content calendar creation"""
    llm = get_claude_llm()
    
    trend_researcher = Agent(
        role='Content Trend Researcher',
        goal='Identify current and upcoming content trends relevant to the target audience',
        backstory="Expert at discovering trending topics and viral content patterns. You find what resonates with audiences.",
        tools=[search_tool, website_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_tokens=100
    )
    
    content_strategist = Agent(
        role='Content Calendar Strategist',
        goal='Develop a strategic 7-day content plan based on research findings',
        backstory="Experienced content strategist who creates balanced, engaging content calendars.",
        tools=[search_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_tokens=100
    )
    
    content_creator = Agent(
        role='Content Creator',
        goal='Generate brief content outlines for each day of the calendar',
        backstory="Creative content developer who transforms plans into actionable content briefs.",
        tools=[search_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_tokens=100
    )
    
    return trend_researcher, content_strategist, content_creator

def create_content_calendar_tasks(researcher, strategist, creator, industry, target_audience, content_goals):
    """Create content calendar tasks with clear objectives but limited scope to manage token usage"""
    # Truncate inputs if they're too long
    industry = industry[:100] if industry else ""
    target_audience = target_audience[:200] if target_audience else ""
    content_goals = content_goals[:200] if content_goals else ""
    
    trend_research_task = Task(
        description=f"""Research current trends in the {industry} industry for {target_audience}.
        
        Focus on:
        1. Top content formats (video, blog, etc.)
        2. Trending topics and hashtags
        3. Upcoming events in the next 2 weeks
        4. 5-7 potential content topics that align with: {content_goals}""",
        agent=researcher,
        expected_output="List of content trends and topic ideas (max 500 words)"
    )
    
    strategy_task = Task(
        description=f"""Create a simple 7-day content calendar for {target_audience} based on the research.
        
        Include:
        1. Mix of content types (educational, promotional, etc.)
        2. One main topic per day
        3. Brief rationale for each day
        
        Format as Day 1: [Topic] - [Type] - [Brief rationale]""",
        agent=strategist,
        context=[trend_research_task],
        expected_output="7-day content calendar outline (max 500 words)"
    )
    
    content_brief_task = Task(
        description=f"""Create brief content outlines for each day of the 7-day calendar.
        
        For each day include:
        1. Headline
        2. Brief hook
        3. 3-5 key points
        4. Call-to-action
        
        Keep each day's brief concise and focused.""",
        agent=creator,
        context=[trend_research_task, strategy_task],
        expected_output="Brief outlines for 7 days of content (max 1000 words)"
    )
    
    return [trend_research_task, strategy_task, content_brief_task]

def create_crew(agents, tasks):
    """Create a crew with optimal settings and token limits"""
    return Crew(
        agents=agents,
        tasks=tasks,
        verbose=True,
        process="sequential",
        max_rpm=10  # Limiting requests per minute to avoid rate limits
    )

def run_content_calendar_creation(industry, target_audience, content_goals):
    """Run the content calendar creation process and return results"""
    try:
        start_time = datetime.now()
        researcher, strategist, creator = create_content_calendar_agents()
        tasks = create_content_calendar_tasks(researcher, strategist, creator, industry, target_audience, content_goals)
        crew = create_crew([researcher, strategist, creator], tasks)
        result = crew.kickoff()
        execution_time = (datetime.now() - start_time).total_seconds()
        return {'result': result, 'execution_time': execution_time}
    except Exception as e:
        return f"Error: {str(e)}"

def save_content_calendar(industry, target_audience, content_goals, result):
    """Save content calendar to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"content_calendar_{timestamp}.json"
    
    data = {
        "industry": industry,
        "target_audience": target_audience,
        "content_goals": content_goals,
        "timestamp": timestamp,
        "content_calendar": str(result)
    }
    
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    
    return filename

def main():
    st.set_page_config(page_title="Skylix Content Calendar", layout="wide")
    
    st.title("📅 Skylix Content Calendar Creator")
    st.subheader("Powered by Claude 3.7 Sonnet")
    
    # Display token usage warning
    st.warning("⚠️ Token Usage Management: Please keep inputs brief to avoid rate limits.")
    
    # Input form with character counters
    with st.form("content_calendar_form"):
        industry = st.text_input("Industry/Niche (max 100 chars)", placeholder="e.g., Fitness, SaaS, Digital Marketing")
        st.caption(f"Characters: {len(industry)}/100")
        
        target_audience = st.text_area("Target Audience (max 200 chars)", placeholder="Key demographics and interests...", height=80)
        st.caption(f"Characters: {len(target_audience)}/200")
        
        content_goals = st.text_area("Content Goals (max 200 chars)", placeholder="e.g., Increase brand awareness...", height=80)
        st.caption(f"Characters: {len(content_goals)}/200")
        
        submit_button = st.form_submit_button("Generate 7-Day Content Calendar")
    
    if submit_button:
        if not industry or not target_audience or not content_goals:
            st.error("Please fill out all fields")
            return
        
        # Create progress tracking
        progress_container = st.empty()
        progress_bar = st.progress(0)
        status_container = st.empty()
        timer_container = st.empty()
        
        status_container.info("Starting content calendar creation...")
        start_time = datetime.now()
        
        # Update timer in a separate area
        def update_timer():
            while True:
                elapsed = (datetime.now() - start_time).total_seconds()
                timer_container.text(f"⏱️ Time elapsed: {elapsed:.1f}s")
                time.sleep(0.5)
        
        import threading
        import time
        timer_thread = threading.Thread(target=update_timer)
        timer_thread.daemon = True
        timer_thread.start()
        
        # Run the content calendar creation
        result = run_content_calendar_creation(industry, target_audience, content_goals)
        
        if isinstance(result, dict):
            # Save results to file
            filename = save_content_calendar(industry, target_audience, content_goals, result['result'])
            
            # Show results
            progress_bar.progress(100)
            status_container.success("Content Calendar Created!")
            timer_container.text(f"⏱️ Total time: {result['execution_time']:.2f}s")
            
            st.subheader("Your 7-Day Content Calendar")
            st.write(result['result'])
            
            # Create a download button for the JSON file
            with open(filename, "r") as f:
                st.download_button(
                    label="Download Content Calendar (JSON)",
                    data=f,
                    file_name=filename,
                    mime="application/json"
                )
            
            # Display the calendar in a more visual format if possible
            try:
                # This is a basic attempt to extract calendar data - actual format may vary
                days = str(result['result']).split("Day ")
                if len(days) > 1:
                    calendar_data = []
                    for day in days[1:]:  # Skip first empty split
                        day_content = day.strip()
                        if day_content:
                            day_num = day_content[0]
                            content = day_content[1:].strip()
                            calendar_data.append({"Day": int(day_num), "Content": content})
                    
                    if calendar_data:
                        st.subheader("Calendar View")
                        calendar_df = pd.DataFrame(calendar_data)
                        st.dataframe(calendar_df)
            except:
                # If parsing fails, just show raw result
                pass
            
        else:
            progress_bar.progress(100)
            status_container.error(f"Error: {result}")
            timer_container.empty()

if __name__ == "__main__":
    main()
