import os
import streamlit as st
from typing import TypedDict, List, Annotated
import operator
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()

# --- State Definition ---
class ResearchState(TypedDict):
    task: str
    plan: str
    content: List[str]
    draft: str
    critique: str
    revision_count: int
    max_revisions: int

# --- Nodes ---

def planner_node(state: ResearchState):
    print("--- PLANNER ---")
    llm = ChatOpenAI(
        model="deepseek/deepseek-chat", 
        temperature=0,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    messages = [
        SystemMessage(content="You are a Research Planner. Given a topic, create a concise step-by-step research plan. Focus on 3-5 key areas to investigate."),
        HumanMessage(content=state['task'])
    ]
    
    response = llm.invoke(messages)
    return {"plan": response.content}

def researcher_node(state: ResearchState):
    print("--- RESEARCHER ---")
    # In a real production app, we would use a Search Tool here.
    # For this demo, we will simulate research using the LLM's internal knowledge 
    # but structured as if it found external info. 
    # This ensures it runs without extra API keys for search if the user doesn't have them,
    # but we could easily swap this for Tavily/Serper.
    
    llm = ChatOpenAI(
        model="deepseek/deepseek-chat", 
        temperature=0.2,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    prompt = f"""You are a Research Specialist. 
    Execute the following research plan:
    {state['plan']}
    
    For each point, provide detailed, factual information. 
    If you were using a search engine, you would look for recent data. 
    Since you are an LLM, use your internal knowledge to provide the most accurate and comprehensive info you have.
    """
    
    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    
    # Append to existing content
    current_content = state.get('content', [])
    return {"content": [response.content]}

def writer_node(state: ResearchState):
    print("--- WRITER ---")
    llm = ChatOpenAI(
        model="deepseek/deepseek-chat", 
        temperature=0.5,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    content_text = "\n\n".join(state['content'])
    
    prompt = f"""You are a Senior Technical Writer. 
    Write a comprehensive report based on the following research:
    
    {content_text}
    
    The report should be well-structured with headers, bullet points, and a clear conclusion.
    Topic: {state['task']}
    """
    
    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    return {"draft": response.content, "revision_count": state.get("revision_count", 0) + 1}

def reviewer_node(state: ResearchState):
    print("--- REVIEWER ---")
    llm = ChatOpenAI(
        model="deepseek/deepseek-chat", 
        temperature=0,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    prompt = f"""You are an Editor in Chief. 
    Review the following draft for clarity, depth, and structure.
    
    Draft:
    {state['draft']}
    
    Provide a critique. If the draft is excellent, say "APPROVE". 
    If it needs work, list specific improvements needed.
    """
    
    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    return {"critique": response.content}

def reviser_node(state: ResearchState):
    print("--- REVISER ---")
    llm = ChatOpenAI(
        model="deepseek/deepseek-chat", 
        temperature=0.5,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    prompt = f"""You are a Senior Writer. 
    Revise your draft based on the editor's critique.
    
    Original Draft:
    {state['draft']}
    
    Critique:
    {state['critique']}
    
    Return the polished final version.
    """
    
    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    return {"draft": response.content}

# --- Conditional Logic ---
def should_continue(state: ResearchState):
    critique = state['critique']
    count = state['revision_count']
    max_revs = state['max_revisions']
    
    if "APPROVE" in critique or count >= max_revs:
        return "end"
    return "revise"

# --- Graph Construction ---
def build_graph():
    workflow = StateGraph(ResearchState)
    
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("reviser", reviser_node)
    
    workflow.set_entry_point("planner")
    
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "writer")
    workflow.add_edge("writer", "reviewer")
    
    workflow.add_conditional_edges(
        "reviewer",
        should_continue,
        {
            "end": END,
            "revise": "reviser"
        }
    )
    
    workflow.add_edge("reviser", "reviewer")
    
    return workflow.compile()

# --- Streamlit App ---
def main():
    st.set_page_config(page_title="Deep Research Agent", layout="wide")
    st.title("🧠 Deep Research Agent")
    st.markdown("Powered by **LangGraph**. This agent Plans, Researches, Writes, Reviews, and Revises iteratively.")
    
    if not os.getenv("OPENAI_API_KEY"):
        st.warning("⚠️ OPENAI_API_KEY not found in .env file.")
        st.stop()
        
    topic = st.text_input("Enter a research topic:", placeholder="e.g., The Future of AI Agents in Enterprise")
    max_revisions = st.slider("Max Revisions", 1, 5, 2)
    
    if st.button("Start Deep Research"):
        if not topic:
            st.error("Please enter a topic.")
            return
            
        graph = build_graph()
        
        status_container = st.container()
        result_container = st.container()
        
        with status_container:
            st.info("🚀 Initializing Agent Workflow...")
            
            # Run the graph
            inputs = {
                "task": topic,
                "max_revisions": max_revisions,
                "revision_count": 0,
                "content": []
            }
            
            # We'll stream the updates to show progress
            try:
                for output in graph.stream(inputs):
                    for key, value in output.items():
                        st.write(f"✅ Finished Step: **{key.upper()}**")
                        with st.expander(f"See {key} output"):
                            st.json(value)
                            
                # Get final state (simulated since stream yields partials)
                # In a real app we'd capture the final output from the stream loop
                
                st.success("Research Complete!")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                
        # Since we can't easily get the final state from the simple stream loop above without logic,
        # we'll just re-run or rely on the last output. 
        # Actually, let's just grab the last 'draft' from the expanders or run invoke() instead of stream() for simplicity if we want just the result.
        # But stream() is cooler. 
        # Let's run invoke() to get the final artifact cleanly for the result container.
        
        with st.spinner("Finalizing report..."):
            final_state = graph.invoke(inputs)
            
        with result_container:
            st.divider()
            st.header("📄 Final Report")
            st.markdown(final_state['draft'])
            
            st.download_button(
                "Download Report",
                data=final_state['draft'],
                file_name="research_report.md",
                mime="text/markdown"
            )

if __name__ == "__main__":
    main()
