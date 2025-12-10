import os
import streamlit as st
from dotenv import load_dotenv

# Fix for Windows signal issue with CrewAI
import platform
import signal
if platform.system() == 'Windows':
    # Mock signals that are missing on Windows
    if not hasattr(signal, 'SIGHUP'):
        signal.SIGHUP = 1
    if not hasattr(signal, 'SIGUSR1'):
        signal.SIGUSR1 = 10
    if not hasattr(signal, 'SIGTSTP'):
        signal.SIGTSTP = 20
    if not hasattr(signal, 'SIGCONT'):
        signal.SIGCONT = 18

    # Force signal.signal to be a no-op to avoid "signal only works in main thread" error
    # which happens when Streamlit (threaded) tries to use CrewAI (uses signals)
    def noop_signal(*args, **kwargs):
        pass
    signal.signal = noop_signal

from crewai import Agent, Task, Crew, LLM
from langchain_openai import ChatOpenAI
from crewai_tools import SerperDevTool, WebsiteSearchTool

# Load environment variables
load_dotenv()
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize tools
search_tool = SerperDevTool()
web_search_tool = WebsiteSearchTool()

def get_llm():
    """Setup LLM with appropriate configuration."""
    # Use LangChain's ChatOpenAI directly to bypass CrewAI's LiteLLM wrapper issues
    return ChatOpenAI(
        model="deepseek/deepseek-chat",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7
    )

def create_agents():
    """Create specialized startup validation agents."""
    # Get the LLM
    llm = get_llm()
    
    # Market Research Analyst
    market_analyst = Agent(
        role='Market Research Analyst',
        goal='Research market size, trends, and competitive landscape for startup ideas',
        backstory='''You are an experienced market research analyst who specializes in emerging 
                    industries and technology trends. You have a keen eye for identifying market 
                    opportunities and potential red flags. You excel at analyzing TAM, SAM, and 
                    SOM for new ventures.''',
        tools=[search_tool, web_search_tool],
        llm=llm,
        verbose=True
    )
    
    # Startup Ecosystem Expert
    ecosystem_expert = Agent(
        role='Startup Ecosystem Expert',
        goal='Analyze similar startups, funding patterns, and YC/accelerator trends',
        backstory='''You have deep knowledge of the startup ecosystem, including Y Combinator, 
                    Techstars, and other major accelerators. You stay up-to-date with funding 
                    rounds, acquisitions, and startup failures. You can identify patterns in 
                    what kinds of startups get funded and succeed.''',
        tools=[search_tool, web_search_tool],
        llm=llm,
        verbose=True
    )
    
    # Business Model Strategist
    business_strategist = Agent(
        role='Business Model Strategist',
        goal='Evaluate business models, revenue streams, and go-to-market strategies',
        backstory='''You are a business strategist with experience in designing sustainable 
                    business models. You understand various revenue models, pricing strategies, 
                    customer acquisition channels, and go-to-market approaches. You can assess 
                    the viability of a business model and suggest improvements.''',
        tools=[search_tool],
        llm=llm,
        verbose=True
    )
    
    # Investment Analyst
    investment_analyst = Agent(
        role='Startup Investment Analyst',
        goal='Assess investment potential, valuation aspects, and investor appeal',
        backstory='''You've worked with venture capital firms and angel investors, evaluating 
                    hundreds of pitch decks and investment opportunities. You understand what 
                    investors look for in early-stage startups and can identify red flags as 
                    well as promising signals.''',
        tools=[search_tool],
        llm=llm,
        verbose=True
    )
    
    return market_analyst, ecosystem_expert, business_strategist, investment_analyst

def create_tasks(market_analyst, ecosystem_expert, business_strategist, investment_analyst, startup_info):
    """Create tasks for each agent based on startup information."""
    
    # Task 1: Market Research Analysis
    market_research = Task(
        description=f'''Research and analyze the market for a startup with the following details:
            - Industry: {startup_info['industry']}
            - Product/Service: {startup_info['product_description']}
            - Target Customers: {startup_info['target_customers']}
            - Problem Statement: {startup_info['problem_statement']}
            
            Provide comprehensive market research including:
            1. Total Addressable Market (TAM) size and growth rate
            2. Serviceable Available Market (SAM) analysis
            3. Key market trends and future outlook
            4. Main competitors and their market share
            5. Market entry barriers
            6. Regulatory considerations
            7. Market validation indicators or red flags''',
        agent=market_analyst,
        expected_output="A detailed market analysis report with quantitative and qualitative data"
    )
    
    # Task 2: Startup Ecosystem Analysis
    ecosystem_analysis = Task(
        description=f'''Analyze similar startups and ecosystem patterns for this idea:
            - Industry: {startup_info['industry']}
            - Product/Service: {startup_info['product_description']}
            - Business Model: {startup_info['business_model']}
            - Unique Value Proposition: {startup_info['value_proposition']}
            
            Research and provide:
            1. Similar startups that have been funded in the last 3 years
            2. Startups in this space that have been accepted to Y Combinator, Techstars, or other major accelerators
            3. Success stories and failure cases in this domain
            4. Current funding trends for this type of startup
            5. Insights from YC partners or prominent VCs about this space
            6. Potential acquirers if the startup succeeds
            7. Red flags based on previous failures in this space''',
        agent=ecosystem_expert,
        context=[market_research],
        expected_output="A comprehensive analysis of the startup ecosystem relevant to this idea"
    )
    
    # Task 3: Business Model Evaluation
    business_model = Task(
        description=f'''Evaluate the business model and go-to-market strategy:
            - Revenue Model: {startup_info['revenue_model']}
            - Pricing Strategy: {startup_info['pricing']}
            - Customer Acquisition Strategy: {startup_info['acquisition_strategy']}
            - Unit Economics: {startup_info['unit_economics']}
            - Unique Value Proposition: {startup_info['value_proposition']}
            
            Analyze and provide:
            1. Viability assessment of the proposed business model
            2. Comparative analysis with business models of successful companies in this space
            3. Potential alternative or complementary revenue streams
            4. Go-to-market strategy recommendations
            5. Customer acquisition cost (CAC) and lifetime value (LTV) considerations
            6. Scalability assessment
            7. Potential pivots if the original model faces challenges''',
        agent=business_strategist,
        context=[market_research, ecosystem_analysis],
        expected_output="A detailed business model evaluation with actionable recommendations"
    )
    
    # Task 4: Investment Potential Assessment
    investment_assessment = Task(
        description=f'''Assess the investment potential and create a final recommendation:
            - Founding Team: {startup_info['team_background']}
            - Funding Needs: {startup_info['funding_needs']}
            - Current Traction: {startup_info['current_traction']}
            - Competitive Advantage: {startup_info['competitive_advantage']}
            - Timeline: {startup_info['timeline']}
            
            Drawing on all previous analyses, provide:
            1. Overall investment attractiveness on a scale of 1-10 with justification
            2. Key strengths of the startup idea
            3. Critical risks and weaknesses to address
            4. Potential valuation range based on comparable companies
            5. Recommended next steps for the founding team
            6. Specific metrics investors would want to see before investing
            7. Types of investors likely to be interested (angels, seed VCs, etc.)
            8. Final recommendation: Proceed, Pivot, or Reconsider''',
        agent=investment_analyst,
        context=[market_research, ecosystem_analysis, business_model],
        expected_output="A comprehensive investment assessment and final recommendation"
    )
    
    return [market_research, ecosystem_analysis, business_model, investment_assessment]

def create_crew(agents, tasks):
    """Create the CrewAI crew with the specified agents and tasks."""
    return Crew(
        agents=agents,
        tasks=tasks,
        verbose=True,
        planning=True,  # Enable planning for better coordination between agents
        memory=True     # Enable memory for agents to remember context from previous tasks
    )

def run_startup_validator(startup_info):
    """Run the startup validator with the provided information."""
    try:
        # Create agents
        market_analyst, ecosystem_expert, business_strategist, investment_analyst = create_agents()
        
        # Create tasks
        tasks = create_tasks(market_analyst, ecosystem_expert, business_strategist, investment_analyst, startup_info)
        
        # Create crew with planning enabled for better coordination
        crew = create_crew([market_analyst, ecosystem_expert, business_strategist, investment_analyst], tasks)
        
        # Execute the crew
        with st.spinner('Our startup validation team is analyzing your idea. This may take a few minutes...'):
            result = crew.kickoff()
            
            # Convert the CrewOutput to string if it's not already
            if hasattr(result, 'raw'):
                result = result.raw
            elif not isinstance(result, str):
                result = str(result)
        
        return result
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def app():
    """Main Streamlit application."""
    st.set_page_config(page_title="Startup Idea Validator", page_icon="🚀", layout="wide")
    
    st.title("🚀 Startup Idea Validator")
    st.markdown("""
    Get comprehensive validation of your startup idea through market research, ecosystem analysis, 
    business model evaluation, and investment potential assessment.
    Our AI team will analyze your idea from multiple perspectives to provide insights and recommendations.
    """)
    
    # Create tabs for organization
    tab1, tab2, tab3 = st.tabs(["Idea Basics", "Business Model", "Team & Traction"])
    
    with tab1:
        st.header("Startup Concept")
        col1, col2 = st.columns(2)
        
        with col1:
            industry = st.selectbox(
                "Industry", 
                ["SaaS", "FinTech", "HealthTech", "EdTech", "E-commerce", "AI/ML", 
                 "CleanTech", "Consumer App", "Hardware", "Marketplace", "Other"]
            )
            
            if industry == "Other":
                industry = st.text_input("Specify Industry")
                
            problem_statement = st.text_area(
                "Problem Statement",
                placeholder="Describe the problem your startup aims to solve..."
            )
            
        with col2:
            product_description = st.text_area(
                "Product/Service Description",
                placeholder="Describe your product or service in detail..."
            )
            
            target_customers = st.text_area(
                "Target Customers",
                placeholder="Describe your ideal customer segments..."
            )
    
    with tab2:
        st.header("Business Model")
        
        col1, col2 = st.columns(2)
        
        with col1:
            business_model = st.selectbox(
                "Business Model Type",
                ["SaaS", "Marketplace", "E-commerce", "Subscription", "Freemium", 
                 "Transaction Fee", "Advertising", "Hardware", "Data/API", "Other"]
            )
            
            if business_model == "Other":
                business_model = st.text_input("Specify Business Model")
            
            revenue_model = st.text_area(
                "Revenue Model Details",
                placeholder="Explain how your startup will generate revenue..."
            )
            
            pricing = st.text_area(
                "Pricing Strategy",
                placeholder="Explain your pricing structure and strategy..."
            )
        
        with col2:
            acquisition_strategy = st.text_area(
                "Customer Acquisition Strategy",
                placeholder="How will you acquire customers? What channels will you use?"
            )
            
            unit_economics = st.text_area(
                "Unit Economics",
                placeholder="Share any information about CAC, LTV, margins, etc. (if available)"
            )
            
            value_proposition = st.text_area(
                "Unique Value Proposition",
                placeholder="What makes your solution unique? Why would customers choose you over alternatives?"
            )
    
    with tab3:
        st.header("Team & Traction")
        
        col1, col2 = st.columns(2)
        
        with col1:
            team_background = st.text_area(
                "Team Background",
                placeholder="Describe founders' experience, skills, and relevant background..."
            )
            
            current_traction = st.text_area(
                "Current Traction",
                placeholder="Describe any users, revenue, pilots, waitlist, or other traction metrics..."
            )
            
            funding_needs = st.text_input(
                "Funding Needs (if any)",
                placeholder="E.g., $500K seed round"
            )
        
        with col2:
            competitive_advantage = st.text_area(
                "Competitive Advantage",
                placeholder="What sustainable advantages do you have over potential competitors?"
            )
            
            timeline = st.text_area(
                "Timeline & Milestones",
                placeholder="Share your key milestones and timeline for the next 12-18 months"
            )
            
            additional_info = st.text_area(
                "Additional Information",
                placeholder="Any other relevant details you'd like our validation team to consider"
            )
    
    # Collect all startup information
    startup_info = {
        "industry": industry,
        "problem_statement": problem_statement,
        "product_description": product_description,
        "target_customers": target_customers,
        "business_model": business_model,
        "revenue_model": revenue_model,
        "pricing": pricing,
        "acquisition_strategy": acquisition_strategy,
        "unit_economics": unit_economics or "Not provided",
        "value_proposition": value_proposition,
        "team_background": team_background,
        "current_traction": current_traction or "Pre-launch",
        "funding_needs": funding_needs or "Not specified",
        "competitive_advantage": competitive_advantage,
        "timeline": timeline or "Not provided",
        "additional_info": additional_info or "None"
    }
    
    # Check if API keys are present
    if not os.getenv("SERPER_API_KEY") or not os.getenv("OPENAI_API_KEY"):
        st.warning("⚠️ API keys not detected. Please add your SERPER_API_KEY and OPENAI_API_KEY to your .env file.")
    
    # Create a submission button
    if st.button("Validate Startup Idea"):
        required_fields = ["problem_statement", "product_description", "target_customers", "value_proposition"]
        missing_fields = [field for field in required_fields if not startup_info[field]]
        
        if missing_fields:
            st.error(f"Please fill in the following required fields: {', '.join(missing_fields)}")
            return
        
        # Display startup information summary
        with st.expander("Summary of Your Startup Information"):
            st.json(startup_info)
        
        # Run the startup validator
        result = run_startup_validator(startup_info)
        
        if result:
            st.success("✅ Your startup idea validation is complete!")
            st.markdown("## Startup Validation Report")
            st.markdown(result)
            
            # Add download capability
            try:
                st.download_button(
                    label="Download Validation Report",
                    data=result,
                    file_name="startup_validation_report.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"Could not generate download button: {str(e)}")
                st.info("You can copy the report text manually from above.")

if __name__ == "__main__":
    app()