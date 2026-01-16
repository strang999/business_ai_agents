import os
import json
import streamlit as st
import time
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import base64
from io import BytesIO

# Import OpenAI Python SDK
import openai
from openai import OpenAI

# Import OpenAI Agents SDK with proper imports based on documentation
from openai import Agent, AgentRunner
from openai.types.beta.thread import Message
from openai.tool import function_tool
from openai.tools.web_search import WebSearchTool
from openai.tools.file_search import FileSearchTool

# Create a directory for storing knowledge base files if it doesn't exist
KNOWLEDGE_BASE_DIR = Path("knowledge_base")
KNOWLEDGE_BASE_DIR.mkdir(exist_ok=True)

# Set up Vector Store for file search if not already created
def setup_vector_store():
    client = OpenAI()
    # Check if we already have a vector store
    vector_stores = client.vector_stores.list()
    vector_store_id = None
    
    # Look for our research agent vector store
    for vs in vector_stores.data:
        if vs.name == "research_agent_files":
            vector_store_id = vs.id
            break
    
    # Create a new vector store if one doesn't exist
    if not vector_store_id:
        vector_store = client.vector_stores.create(name="research_agent_files")
        vector_store_id = vector_store.id
    
    return vector_store_id

# Upload a file to the vector store
def upload_file_to_vector_store(file_path, vector_store_id):
    client = OpenAI()
    
    # First upload the file to get a file ID
    with open(file_path, "rb") as file:
        file_obj = client.files.create(
            file=file,
            purpose="assistants"
        )
    
    # Add the file to the vector store
    client.vector_stores.files.create(
        vector_store_id=vector_store_id,
        file_id=file_obj.id
    )
    
    return file_obj.id

# Create Research Agent using Agents SDK
def create_research_agent(model="gpt-4o-mini"):
    # Set up tools
    web_search_tool = WebSearchTool()
    
    # Create the agent with web search capability
    agent = Agent(
        name="Research Assistant",
        instructions="""You are a highly efficient research assistant that helps users find and synthesize information. 
        Your goal is to provide comprehensive, accurate, and well-cited answers to research questions.
        
        When given a research task:
        1. Break down complex questions into manageable parts
        2. Use web search to find the most current and relevant information
        3. If file search is available, look for relevant information in the user's knowledge base
        4. Synthesize information from multiple sources
        5. Always cite your sources with proper links
        6. Provide balanced perspectives on controversial topics
        7. Clarify when information might be outdated or uncertain
        8. When appropriate, suggest follow-up questions or areas for further research
        
        Respond in a clear, organized manner with headings and sections for complex topics.
        """,
        model=model,
        tools=[web_search_tool]
    )
    
    return agent

# Create a File Search Agent that specifically searches through the vector store
def create_file_search_agent(vector_store_id, model="gpt-4o-mini"):
    # Set up the file search tool with the vector store
    file_search_tool = FileSearchTool(vector_store_ids=[vector_store_id])
    
    # Create the agent
    agent = Agent(
        name="File Search Assistant",
        instructions="""You are a knowledge base search specialist that helps find information in the user's documents.
        Use the file search tool to locate relevant information in the user's knowledge base.
        Provide accurate information based only on the content of the files.
        Always cite which file the information came from.
        If you can't find relevant information in the files, clearly state that.
        """,
        model=model,
        tools=[file_search_tool]
    )
    
    return agent

# Create a main orchestrator agent that can delegate to specialized agents
def create_orchestrator_agent(file_search_agent, model="gpt-4o-mini"):
    # Define a function to handle research with file search
    @function_tool
    async def research_with_files(query: str) -> str:
        """
        Research a topic using the knowledge base files.
        """
        trace = await AgentRunner.run(file_search_agent, query)
        return trace.final_output
    
    # Set up web search
    web_search_tool = WebSearchTool()
    
    # Create the orchestrator agent
    agent = Agent(
        name="Research Orchestrator",
        instructions="""You are a comprehensive research assistant that coordinates different specialized tools to help users.
        
        For general research questions, use web search first to find up-to-date information.
        
        When a user asks about information that might be in their knowledge base or private documents, use the research_with_files tool.
        
        Always consider which tool is most appropriate for the task:
        - Web search for current events, general knowledge, or public information
        - File search for personal documents or specialized knowledge base content
        
        Provide comprehensive, well-organized answers with proper citations.
        """,
        model=model,
        tools=[web_search_tool, research_with_files]
    )
    
    return agent

# Run a research query using the appropriate agent(s)
async def run_research(query, agent, include_trace=False):
    # Execute the research
    trace = await AgentRunner.run(agent, query)
    
    # Extract results
    result = {
        "text": trace.final_output,
        "sources": []
    }
    
    # Try to extract sources from the trace
    try:
        # Extract web search URLs if present
        for event in trace.events:
            if event.name == "tool_call" and event.data.get("tool_name") == "web_search":
                web_results = event.data.get("output", {}).get("web_results", [])
                if web_results:
                    for web_result in web_results:
                        if web_result.get("url") and web_result.get("title"):
                            result["sources"].append({
                                "title": web_result.get("title"),
                                "url": web_result.get("url")
                            })
            
            # Extract file search sources if present
            elif event.name == "tool_call" and event.data.get("tool_name") == "file_search":
                file_results = event.data.get("output", {}).get("results", [])
                if file_results:
                    for file_result in file_results:
                        if file_result.get("file_id") and file_result.get("file_name"):
                            result["sources"].append({
                                "title": file_result.get("file_name"),
                                "file_id": file_result.get("file_id")
                            })
    except Exception as e:
        print(f"Error extracting sources: {e}")
    
    # Include the trace if requested
    if include_trace:
        result["trace"] = trace
    
    return result

# Streamlit UI
def main():
    st.set_page_config(page_title="Research Agent", page_icon="🔍", layout="wide")
    
    # Check if OpenAI API key is set
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            st.sidebar.success("API key set successfully!")
        else:
            st.error("Please enter your OpenAI API key in the sidebar to continue.")
            return
    
    st.title("Research Agent with OpenAI Agents SDK")
    st.markdown("This application uses the OpenAI Agents SDK to conduct research using web search and file search capabilities.")
    
    # Sidebar configuration options
    st.sidebar.header("Configuration")
    
    # Model selection
    model = st.sidebar.selectbox(
        "Select Model",
        ["gpt-4o-mini", "gpt-4o"],
        index=0
    )
    
    # Initialize session state
    if 'vector_store_id' not in st.session_state:
        try:
            with st.spinner("Setting up knowledge base..."):
                st.session_state.vector_store_id = setup_vector_store()
        except Exception as e:
            st.error(f"Error setting up vector store: {str(e)}")
            st.session_state.vector_store_id = None
    
    if 'research_agent' not in st.session_state or st.session_state.get('current_model') != model:
        with st.spinner("Initializing research agent..."):
            st.session_state.research_agent = create_research_agent(model=model)
            if st.session_state.vector_store_id:
                st.session_state.file_search_agent = create_file_search_agent(st.session_state.vector_store_id, model=model)
                st.session_state.orchestrator_agent = create_orchestrator_agent(
                    st.session_state.file_search_agent,
                    model=model
                )
            st.session_state.current_model = model
    
    # Helper function to run async functions in Streamlit
    def run_async(coroutine):
        return asyncio.run(coroutine)
    
    # Tabs for different features
    tab1, tab2, tab3 = st.tabs([
        "Research", 
        "Knowledge Base", 
        "Trace Viewer"
    ])
    
    # Research Tab
    with tab1:
        st.header("Research Assistant")
        
        # Agent selection
        agent_type = st.radio(
            "Select research mode:",
            ["Web Search", "File Search", "Combined (Orchestrator)"],
            horizontal=True,
            disabled=not st.session_state.vector_store_id and (agent_type in ["File Search", "Combined (Orchestrator)"])
        )
        
        if not st.session_state.vector_store_id and agent_type in ["File Search", "Combined (Orchestrator)"]:
            st.warning("Vector store not available. Please check your setup.")
            agent_type = "Web Search"
        
        query = st.text_area("Research query:", height=100)
        
        col1, col2 = st.columns([1, 5])
        with col1:
            include_trace = st.checkbox("Include trace", value=False)
        
        with col2:
            if st.button("Research", key="research_button"):
                if query:
                    with st.spinner("Researching..."):
                        try:
                            # Select the appropriate agent
                            if agent_type == "Web Search":
                                research_agent = st.session_state.research_agent
                            elif agent_type == "File Search":
                                if st.session_state.vector_store_id:
                                    research_agent = st.session_state.file_search_agent
                                else:
                                    st.error("File search not available - falling back to web search")
                                    research_agent = st.session_state.research_agent
                            else:  # Combined
                                if st.session_state.vector_store_id:
                                    research_agent = st.session_state.orchestrator_agent
                                else:
                                    st.error("Orchestrator not available - falling back to web search")
                                    research_agent = st.session_state.research_agent
                            
                            # Run the research
                            results = run_async(run_research(query, research_agent, include_trace))
                            
                            # Display results
                            st.markdown("## Research Results")
                            st.write(results["text"])
                            
                            # Display sources if available
                            if results["sources"]:
                                st.markdown("### Sources")
                                for i, source in enumerate(results["sources"], 1):
                                    if "url" in source:
                                        st.markdown(f"{i}. [{source['title']}]({source['url']})")
                                    elif "file_id" in source:
                                        st.markdown(f"{i}. File: {source['title']}")
                            
                            # Store trace for viewing
                            if include_trace and "trace" in results:
                                st.session_state.last_trace = results["trace"]
                                st.info("Trace captured and available in the Trace Viewer tab.")
                        except Exception as e:
                            st.error(f"Error during research: {str(e)}")
                else:
                    st.warning("Please enter a research query.")
    
    # Knowledge Base Tab
    with tab2:
        st.header("Knowledge Base Management")
        
        if not st.session_state.vector_store_id:
            st.error("Vector store is not available. Please check your API key and permissions.")
        else:
            # Display files in knowledge base
            st.subheader("Upload Files to Knowledge Base")
            
            uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx", "csv", "json", "md"])
            
            if uploaded_file is not None:
                # Save the uploaded file temporarily
                file_path = os.path.join(KNOWLEDGE_BASE_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Upload to vector store
                if st.button("Add to Knowledge Base"):
                    with st.spinner("Processing file..."):
                        try:
                            file_id = upload_file_to_vector_store(file_path, st.session_state.vector_store_id)
                            st.success(f"File added to knowledge base! File ID: {file_id}")
                        except Exception as e:
                            st.error(f"Error adding file to knowledge base: {str(e)}")
            
            # Display knowledge base files
            st.subheader("Knowledge Base Files")
            
            # Placeholder for listing files in the vector store
            # (In a full implementation, we would list files from the vector store)
            # For now, we'll list local files in the knowledge_base directory
            
            if os.path.exists(KNOWLEDGE_BASE_DIR):
                files = list(KNOWLEDGE_BASE_DIR.glob("*"))
                if files:
                    st.write(f"Files in local knowledge base directory:")
                    for file in files:
                        st.write(f"- {file.name}")
                else:
                    st.info("No files in local knowledge base directory.")
            
            # Add a query box for testing file search
            st.subheader("Test File Search")
            file_query = st.text_input("Query your knowledge base:")
            
            if st.button("Search Files"):
                if file_query:
                    with st.spinner("Searching knowledge base..."):
                        try:
                            results = run_async(run_research(file_query, st.session_state.file_search_agent))
                            
                            st.markdown("### Search Results")
                            st.write(results["text"])
                        except Exception as e:
                            st.error(f"Error searching knowledge base: {str(e)}")
                else:
                    st.warning("Please enter a search query.")
    
    # Trace Viewer Tab
    with tab3:
        st.header("Trace Viewer")
        
        if 'last_trace' in st.session_state:
            trace = st.session_state.last_trace
            
            st.subheader("Trace Information")
            st.write(f"Agent Name: {trace.agent_info.name}")
            st.write(f"Model: {trace.agent_info.model}")
            
            st.subheader("Events")
            for i, event in enumerate(trace.events):
                with st.expander(f"Event {i+1}: {event.name}"):
                    st.write(f"Timestamp: {event.timestamp}")
                    st.write(f"Event Type: {event.name}")
                    
                    # Display different information based on event type
                    if event.name == "tool_call":
                        st.write(f"Tool: {event.data.get('tool_name')}")
                        st.write("Input:")
                        st.code(json.dumps(event.data.get("input"), indent=2), language="json")
                        
                        if "output" in event.data:
                            st.write("Output:")
                            st.code(json.dumps(event.data.get("output"), indent=2), language="json")
                    
                    elif event.name == "agent_message":
                        role = event.data.get("role")
                        content = event.data.get("content")
                        st.write(f"Role: {role}")
                        st.write(f"Content: {content}")
                    
                    # Show all event data for debugging
                    with st.expander("Raw Event Data"):
                        st.code(json.dumps(event.data, indent=2), language="json")
            
            # Display final output
            st.subheader("Final Output")
            st.write(trace.final_output)
        else:
            st.info("No trace available. Run a research query with 'Include trace' checked to see trace data here.")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "This research agent uses the OpenAI Agents SDK to provide comprehensive "
        "research capabilities including web search and file search."
    )
    
    # Instructions for setup
    st.sidebar.markdown("### Setup Guide")
    with st.sidebar.expander("Installation Instructions"):
        st.markdown("""
        To set up this application correctly:
        
        1. Install the required packages:
        ```bash
        pip install openai openai-agents streamlit
        ```
        
        2. Set your OpenAI API key as an environment variable:
        ```bash
        export OPENAI_API_KEY='your-api-key'
        ```
        
        3. Run the Streamlit app:
        ```bash
        streamlit run app.py
        ```
        """)

if __name__ == "__main__":
    main()