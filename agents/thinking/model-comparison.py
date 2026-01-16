import streamlit as st
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool, WebsiteSearchTool
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
import google.generativeai as genai

# Load environment variables
load_dotenv()
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

# Initialize enhanced search tools
search_tool = SerperDevTool()
website_tool = WebsiteSearchTool()

def check_ollama_availability():
    """Check if Ollama server is running"""
    try:
        response = requests.get("http://localhost:11434/api/version")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def get_llm(model_type):
    """Initialize the specified language model"""   
    if model_type == "o3-mini":
        return ChatOpenAI(model_name="o3-mini")
    elif model_type == "gemini":
        return LLM(
            model="gemini/gemini-2.0-flash-001",
            temperature=0.7,
            max_tokens=2048,
            top_p=0.8,
            vertex_credentials=None  # Will use GOOGLE_API_KEY environment variable
        )
    else:  # deepseek
        return LLM(
            model="ollama/deepseek-r1:latest",
            base_url="http://localhost:11434",
            temperature=0.7
        )

def create_agents(model_type):
    """Create specialized research and analysis agents for a specific model"""
    try:
        llm = get_llm(model_type)
        
        researcher = Agent(
            role=f'Deep Research Specialist ({model_type})',
            goal='Conduct comprehensive research and gather detailed information',
            backstory="""Expert researcher skilled at discovering hard-to-find information 
            and connecting complex data points. Specializes in thorough, detailed research.""",
            tools=[search_tool, website_tool],
            llm=llm,
            verbose=True,
            max_iter=15,
            allow_delegation=False
        )
        
        analyst = Agent(
            role=f'Research Analyst ({model_type})',
            goal='Analyze and synthesize research findings',
            backstory="""Expert analyst skilled at processing complex information and 
            identifying key patterns and insights. Specializes in clear, actionable analysis.""",
            tools=[search_tool],
            llm=llm,
            verbose=True,
            max_iter=10,
            allow_delegation=False
        )
        
        writer = Agent(
            role=f'Content Synthesizer ({model_type})',
            goal='Create clear, structured reports from analysis',
            backstory="""Expert writer skilled at transforming complex analysis into 
            clear, engaging content while maintaining technical accuracy.""",
            llm=llm,
            verbose=True,
            max_iter=8,
            allow_delegation=False
        )
        
        return researcher, analyst, writer
    except Exception as e:
        st.error(f"Error creating agents for {model_type}: {str(e)}")
        return None, None, None

def create_tasks(researcher, analyst, writer, topic):
    """Create research tasks with clear objectives"""
    research_task = Task(
        description=f"""Research this topic thoroughly: {topic}
        
        Follow these steps:
        1. Find reliable sources and latest information
        2. Extract key details and evidence
        3. Verify information across sources
        4. Document findings with references""",
        agent=researcher,
        expected_output="Detailed research findings with sources"
    )
    
    analysis_task = Task(
        description=f"""Analyze the research findings about {topic}:
        
        Steps:
        1. Review and categorize findings
        2. Identify patterns and trends
        3. Evaluate source credibility
        4. Note key insights""",
        agent=analyst,
        context=[research_task],
        expected_output="Analysis of findings and insights"
    )
    
    synthesis_task = Task(
        description=f"""Create a clear report on {topic}:
        
        Include:
        - Executive Summary
        - Key Findings
        - Evidence
        - Conclusions
        - Specific questions asked by the user
        - search volume, demand, search conversion
        - Top keywords
        - References""",
        agent=writer,
        context=[research_task, analysis_task],
        expected_output="Structured report with insights"
    )
    
    return [research_task, analysis_task, synthesis_task]

def run_single_model_research(topic, model_type):
    """Execute research process for a single model"""
    try:
        researcher, analyst, writer = create_agents(model_type)
        if not all([researcher, analyst, writer]):
            raise Exception(f"Failed to create agents for {model_type}")
        
        tasks = create_tasks(researcher, analyst, writer, topic)
        crew = Crew(
            agents=[researcher, analyst, writer],
            tasks=tasks,
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)
    except Exception as e:
        return f"Error with {model_type}: {str(e)}"

@st.cache_data(ttl=3600)
def run_parallel_research(topic, selected_models):
    """Execute research process in parallel for multiple models"""
    results = {}
    
    for model in selected_models:
        try:
            with st.spinner(f"🔍 Researching with {model}..."):
                result = run_single_model_research(topic, model)
                results[model] = result
        except Exception as e:
            results[model] = f"Error with {model}: {str(e)}"
    
    return results

def check_api_keys():
    """Check availability of required API keys"""
    api_status = {
        "gpt-4o-mini": bool(os.getenv("OPENAI_API_KEY")),
        "gemini": bool(os.getenv("GEMINI_API_KEY")),
        "deepseek": check_ollama_availability()
    }
    return api_status

def main():
    st.set_page_config(
        page_title="Multi-LLM Research Assistant",
        page_icon="🔍",
        layout="wide"
    )

    # Sidebar settings
    st.sidebar.title("⚙️ Model Selection")
    
    # Check API keys and model availability
    api_status = check_api_keys()
    
    # Model selection with checkboxes
    st.sidebar.markdown("### Choose Models")
    selected_models = []
    
    if api_status["gpt-4o-mini"]:
        if st.sidebar.checkbox("OpenAI GPT-4o-mini", value=True):
            selected_models.append("gpt-4o-mini")
    else:
        st.sidebar.warning("⚠️ OpenAI API key not found")
        
    if api_status["gemini"]:
        if st.sidebar.checkbox("Google Gemini-2.0", value=True):
            selected_models.append("gemini")
    else:
        st.sidebar.warning("⚠️ Google API key not found")
        
    if api_status["deepseek"]:
        if st.sidebar.checkbox("Local DeepSeek-r1", value=True):
            selected_models.append("deepseek")
    else:
        st.sidebar.warning("⚠️ Ollama not running")

    # Main content
    st.title("🔍 Multi-LLM Research Assistant")
    st.markdown("""
    This enhanced research assistant uses multiple AI models in parallel to provide comprehensive, 
    multi-perspective research on any topic. Select one or more models to compare their analyses.
    """)

    # Input
    query = st.text_area(
        "Research Topic",
        placeholder="Enter your research topic (be specific)...",
        help="More specific queries yield better results"
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        start_research = st.button(
            f"🚀 Start Research with {len(selected_models)} Model{'s' if len(selected_models) != 1 else ''}", 
            type="primary",
            disabled=len(selected_models) == 0
        )

    # Execute research
    if start_research and query and selected_models:
        with st.spinner(f"🔍 Conducting research using {len(selected_models)} models..."):
            results = run_parallel_research(query, selected_models)

        st.success("✅ Research Complete!")
        
        # Create tabs for each model plus comparison
        tabs = [f"📊 {model.upper()}" for model in selected_models]
        if len(selected_models) > 1:
            tabs.append("🔄 Comparison")
            
        tab_list = st.tabs(tabs)
        
        # Display individual results
        for i, model in enumerate(selected_models):
            with tab_list[i]:
                st.markdown(f"### Research Report from {model.upper()}")
                st.markdown("---")
                st.markdown(str(results[model]))
        
        # Display comparison if multiple models selected
        if len(selected_models) > 1:
            with tab_list[-1]:
                st.markdown("### Model Comparison")
                st.markdown("---")
                for model in selected_models:
                    with st.expander(f"{model.upper()} Summary"):
                        # Extract and display key points from each model's results
                        st.markdown(str(results[model]))
    
    st.divider()
    st.markdown("*Built with CrewAI, Streamlit, and Multiple LLMs*")

if __name__ == "__main__":
    main()