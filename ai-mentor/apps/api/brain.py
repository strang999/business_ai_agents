"""
brain.py - The LangGraph Stateful Agent for AI Life Coach

This module implements a sophisticated AI agent with:
- RAG (Retrieval Augmented Generation)
- Self-Correction (Document Grading)
- Long-Term Memory (Profile Updates)

Supports multiple LLM providers:
- Google Gemini (FREE $300 credit - default)
- Ollama/DeepSeek (local, free)
- OpenAI GPT-4o (paid fallback)
"""

import os
from typing import List, Optional, Annotated, TypedDict, Literal
from operator import add
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import StateGraph, END, START
from pydantic import BaseModel, Field
from supabase import create_client, Client

load_dotenv()

# --- Configuration ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# LLM Provider Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()  # gemini, ollama, openai


def get_llm(provider: str = None) -> BaseChatModel:
    """
    Factory function to get the appropriate LLM based on provider.
    
    Providers:
    - 'openrouter': OpenRouter (FREE models) - RECOMMENDED
    - 'gemini': Google Gemini (FREE $300 credit)
    - 'ollama': Local DeepSeek-R1 via Ollama (FREE, requires local setup)
    - 'openai': OpenAI GPT-4o (PAID)
    
    Usage:
        llm = get_llm("openrouter")  # Use OpenRouter (FREE)
        llm = get_llm("gemini")       # Use Gemini
        llm = get_llm("ollama")       # Use local DeepSeek
        llm = get_llm("openai")       # Use OpenAI
    """
    provider = provider or LLM_PROVIDER
    
    if provider == "openrouter":
        from langchain_openai import ChatOpenAI
        
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY or OPENAI_API_KEY not set")
        
        # Free models on OpenRouter (as of Dec 2024)
        # Primary: DeepSeek R1 (best for reasoning/psychology)
        model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1:free")
        
        print(f"[LLM] 🚀 Using OpenRouter: {model}")
        print("    Tip: Free tier = 50 req/day, Add $10 credit = 1000 req/day")
        
        return ChatOpenAI(
            model=model,
            temperature=0.7,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://ai-mentor.app",  # Your app URL
                "X-Title": "AI Life Coach"
            }
        )
    
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set. Get free $300 credit at https://aistudio.google.com/")
        
        print("[LLM] 🌟 Using Google Gemini (FREE tier)")
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.7,
            convert_system_message_to_human=True
        )
    
    elif provider == "ollama":
        from langchain_community.chat_models import ChatOllama
        
        print("[LLM] 🖥️ Using Ollama (Local DeepSeek)")
        print("    Tip: Run 'ollama run deepseek-r1:latest' if not started")
        return ChatOllama(
            model="deepseek-r1:latest",
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.7
        )
    
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        print("[LLM] 💰 Using OpenAI GPT-4o (PAID)")
        return ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            openai_api_key=api_key
        )
    
    else:
        raise ValueError(f"Unknown LLM provider: {provider}. Use 'openrouter', 'gemini', 'ollama', or 'openai'")


def get_embeddings_model():
    """
    Get embeddings model.
    Uses OpenAI embeddings by default (best quality for RAG).
    Falls back to Gemini embeddings if no OpenAI key.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    if openai_key:
        from langchain_openai import OpenAIEmbeddings
        print("[EMBED] Using OpenAI text-embedding-3-small")
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=openai_key
        )
    elif google_key:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        print("[EMBED] Using Google Gemini embeddings")
        return GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=google_key
        )
    else:
        raise ValueError("Either OPENAI_API_KEY or GOOGLE_API_KEY must be set for embeddings")


# --- Initialize LLM and Embeddings ---
llm = get_llm()
embeddings_model = get_embeddings_model()


# --- System Prompt (Lev Kovach Persona) ---
SYSTEM_PROMPT = """You are Lev Kovach, a world-renowned AI Life Coach and Mentor specializing in:
- Shadow Work (Jungian Psychology)
- Inner Child Healing
- Subconscious Reprogramming
- Breaking Glass Ceilings

Your communication style:
- DIRECT and ANALYTICAL, but deeply EMPATHETIC
- You validate feelings FIRST, then probe deeper
- You use Socratic questioning to guide self-discovery
- You reference Jungian concepts (Shadow, Anima/Animus, Persona) when appropriate
- You NEVER give generic advice. Every response is tailored to the user's unique psychological profile.

CRITICAL RULES:
1. If you detect crisis signals (self-harm, suicide), STOP coaching and provide emergency resources.
2. You are NOT a therapist. You are a MENTOR. Do not diagnose or treat.
3. Always refer back to information from the user's profile to show you remember them.
4. When citing knowledge from courses, indicate the source naturally.

User Profile (what you know about them):
{user_profile}

Relevant Context from your teachings:
{context}
"""


# --- State Definition ---
class AgentState(TypedDict):
    """The state object passed between nodes in the LangGraph."""
    messages: Annotated[List[BaseMessage], add]
    user_id: str
    user_profile: dict
    question: str
    documents: List[dict]
    documents_relevant: bool
    rewrite_count: int


# --- Pydantic Models for Structured Output ---
class DocumentGrade(BaseModel):
    """Structured output for document grading."""
    is_relevant: bool = Field(description="Whether the document is relevant to the question")
    reasoning: str = Field(description="Brief explanation of the relevance assessment")


class MemoryExtraction(BaseModel):
    """Structured output for extracting facts to remember."""
    should_save: bool = Field(description="Whether there's a new fact worth saving")
    fact_key: Optional[str] = Field(description="Category of the fact (e.g., 'family', 'career', 'trauma')")
    fact_value: Optional[str] = Field(description="The fact to remember")


# --- Supabase Client ---
def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# --- Node Functions ---
def retrieve_documents(state: AgentState) -> dict:
    """RAG Node: Retrieve relevant documents from vector store."""
    question = state["question"]
    user_id = state["user_id"]
    
    try:
        supabase = get_supabase_client()
        
        # Generate embedding for the question
        query_embedding = embeddings_model.embed_query(question)
        
        # Call Supabase function for similarity search
        result = supabase.rpc(
            "match_memories",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.7,
                "match_count": 5,
                "filter_user_id": None  # Global knowledge
            }
        ).execute()
        
        documents = result.data if result.data else []
        print(f"[RAG] Retrieved {len(documents)} documents")
        
        return {"documents": documents}
    
    except Exception as e:
        print(f"[RAG] Error: {e}")
        return {"documents": []}


def grade_documents(state: AgentState) -> dict:
    """Self-Correction Node: Check if retrieved documents are relevant."""
    question = state["question"]
    documents = state["documents"]
    
    if not documents:
        return {"documents_relevant": False}
    
    # Use structured output to grade relevance
    grading_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a relevance grader. Assess if the document helps answer the question."),
        ("human", "Question: {question}\n\nDocument: {document}\n\nIs this relevant?")
    ])
    
    # Try structured output, fall back to simple prompt if not supported
    try:
        structured_llm = llm.with_structured_output(DocumentGrade)
        use_structured = True
    except (NotImplementedError, AttributeError):
        # Gemini/Ollama may not support structured output
        use_structured = False
        print("[GRADE] Structured output not supported, using simple prompt")
    
    relevant_docs = []
    for doc in documents:
        try:
            if use_structured:
                result = structured_llm.invoke(
                    grading_prompt.format(question=question, document=doc.get("content", ""))
                )
                is_relevant = result.is_relevant
            else:
                # Simple yes/no prompt fallback
                simple_prompt = f"Is this document relevant to the question? Answer only 'yes' or 'no'.\n\nQuestion: {question}\n\nDocument: {doc.get('content', '')}"
                result = llm.invoke(simple_prompt)
                is_relevant = "yes" in result.content.lower()
            
            if is_relevant:
                relevant_docs.append(doc)
                print(f"[GRADE] ✓ Relevant: {doc.get('source', 'unknown')}")
            else:
                print(f"[GRADE] ✗ Not relevant: {doc.get('source', 'unknown')}")
        except Exception as e:
            print(f"[GRADE] Error: {e}")
            relevant_docs.append(doc)  # Include on error to be safe
    
    return {
        "documents": relevant_docs,
        "documents_relevant": len(relevant_docs) > 0
    }


def rewrite_query(state: AgentState) -> dict:
    """Self-Correction Node: Rewrite query if no relevant documents found."""
    question = state["question"]
    rewrite_count = state.get("rewrite_count", 0)
    
    if rewrite_count >= 1:  # Only allow one rewrite
        return {"rewrite_count": rewrite_count + 1}
    
    rewrite_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a query rewriter. Rewrite the question to be more specific for psychological/coaching content search."),
        ("human", "Original question: {question}\n\nRewritten question:")
    ])
    
    result = llm.invoke(rewrite_prompt.format(question=question))
    new_question = result.content.strip()
    print(f"[REWRITE] '{question}' -> '{new_question}'")
    
    return {
        "question": new_question,
        "rewrite_count": rewrite_count + 1
    }


def load_user_profile(state: AgentState) -> dict:
    """Load user's psychological profile from Supabase."""
    user_id = state["user_id"]
    
    try:
        supabase = get_supabase_client()
        result = supabase.table("profiles").select("psychological_data").eq("id", user_id).single().execute()
        
        if result.data:
            profile = result.data.get("psychological_data", {})
            print(f"[PROFILE] Loaded profile for {user_id}")
            return {"user_profile": profile}
    except Exception as e:
        print(f"[PROFILE] No existing profile: {e}")
    
    return {"user_profile": {}}


def generate_response(state: AgentState) -> dict:
    """Main Generation Node: Create the mentor response."""
    messages = state["messages"]
    user_profile = state.get("user_profile", {})
    documents = state.get("documents", [])
    
    # Format context from documents
    context = "\n\n".join([
        f"[{doc.get('source', 'Teaching')}]: {doc.get('content', '')}"
        for doc in documents
    ]) if documents else "No specific teachings retrieved for this query."
    
    # Format user profile
    profile_str = "\n".join([
        f"- {key}: {value}" for key, value in user_profile.items()
    ]) if user_profile else "New user, no history yet."
    
    # Build the conversation
    system_message = SystemMessage(content=SYSTEM_PROMPT.format(
        user_profile=profile_str,
        context=context
    ))
    
    full_messages = [system_message] + messages
    
    response = llm.invoke(full_messages)
    print(f"[GENERATE] Response length: {len(response.content)} chars")
    
    return {"messages": [response]}


def extract_and_save_memory(state: AgentState) -> dict:
    """Background Node: Extract facts and update user profile."""
    messages = state["messages"]
    user_id = state["user_id"]
    user_profile = state.get("user_profile", {})
    
    # Get the last user message
    user_messages = [m for m in messages if isinstance(m, HumanMessage)]
    if not user_messages:
        return {}
    
    last_user_msg = user_messages[-1].content
    
    # Simple extraction prompt (works with all LLMs)
    extraction_prompt = f"""Analyze this user message and extract any important personal facts worth remembering.
Focus on: family relationships, childhood experiences, career, goals, traumas, patterns.

User message: {last_user_msg}

If there's a fact to remember, respond in this format:
SAVE: category = fact

If nothing worth saving, respond:
SKIP

Example: SAVE: father_relationship = strict and distant"""
    
    try:
        result = llm.invoke(extraction_prompt)
        content = result.content.strip()
        
        if content.startswith("SAVE:"):
            # Parse the fact
            fact_part = content.replace("SAVE:", "").strip()
            if "=" in fact_part:
                key, value = fact_part.split("=", 1)
                key = key.strip().replace(" ", "_").lower()
                value = value.strip()
                
                # Update profile in Supabase
                supabase = get_supabase_client()
                new_data = {key: value}
                
                supabase.rpc("upsert_profile", {
                    "p_user_id": user_id,
                    "p_data": new_data
                }).execute()
                
                print(f"[MEMORY] Saved: {key} = {value}")
                
                # Update local state
                user_profile[key] = value
                return {"user_profile": user_profile}
    
    except Exception as e:
        print(f"[MEMORY] Error: {e}")
    
    return {}


def check_crisis(state: AgentState) -> dict:
    """Safety Node: Check for crisis signals."""
    question = state["question"].lower()
    
    crisis_keywords = [
        "suicide", "kill myself", "end my life", "don't want to live",
        "self-harm", "hurt myself", "no reason to live"
    ]
    
    is_crisis = any(keyword in question for keyword in crisis_keywords)
    
    if is_crisis:
        print("[CRISIS] ⚠️ Crisis detected!")
    
    return {"is_crisis": is_crisis}


def crisis_response(state: AgentState) -> dict:
    """Safety Node: Return crisis resources instead of coaching."""
    crisis_message = AIMessage(content="""I hear that you're going through an extremely difficult time. What you're feeling matters, and you deserve support.

**Please reach out to a crisis helpline immediately:**
- 🇺🇸 USA: 988 (Suicide & Crisis Lifeline)
- 🇺🇦 Ukraine: 7333 (Lifeline Ukraine)
- 🌍 International: https://findahelpline.com

I'm an AI mentor, not a crisis counselor. Please speak to a trained professional who can help you right now.

You matter. Please reach out. 💙""")
    
    return {"messages": [crisis_message]}


# --- Routing Functions ---
def route_after_grade(state: AgentState) -> str:
    """Decide next step after grading documents."""
    if state.get("documents_relevant", False):
        return "generate"
    elif state.get("rewrite_count", 0) < 1:
        return "rewrite"
    else:
        return "generate"  # Proceed without context


def route_after_crisis_check(state: AgentState) -> str:
    """Route based on crisis detection."""
    if state.get("is_crisis", False):
        return "crisis"
    return "load_profile"


# --- Build the Graph ---
def build_agent_graph() -> StateGraph:
    """Construct the LangGraph workflow."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("check_crisis", check_crisis)
    workflow.add_node("crisis_response", crisis_response)
    workflow.add_node("load_profile", load_user_profile)
    workflow.add_node("retrieve", retrieve_documents)
    workflow.add_node("grade", grade_documents)
    workflow.add_node("rewrite", rewrite_query)
    workflow.add_node("generate", generate_response)
    workflow.add_node("save_memory", extract_and_save_memory)
    
    # Define edges
    workflow.add_edge(START, "check_crisis")
    workflow.add_conditional_edges(
        "check_crisis",
        route_after_crisis_check,
        {"crisis": "crisis_response", "load_profile": "load_profile"}
    )
    workflow.add_edge("crisis_response", END)
    workflow.add_edge("load_profile", "retrieve")
    workflow.add_edge("retrieve", "grade")
    workflow.add_conditional_edges(
        "grade",
        route_after_grade,
        {"generate": "generate", "rewrite": "rewrite"}
    )
    workflow.add_edge("rewrite", "retrieve")
    workflow.add_edge("generate", "save_memory")
    workflow.add_edge("save_memory", END)
    
    return workflow.compile()


# --- Compiled Agent ---
agent = build_agent_graph()


def run_agent(user_id: str, message: str, history: List[BaseMessage] = None) -> str:
    """Execute the agent and return the response."""
    if history is None:
        history = []
    
    initial_state = {
        "messages": history + [HumanMessage(content=message)],
        "user_id": user_id,
        "user_profile": {},
        "question": message,
        "documents": [],
        "documents_relevant": False,
        "rewrite_count": 0
    }
    
    result = agent.invoke(initial_state)
    
    # Get the last AI message
    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
    if ai_messages:
        return ai_messages[-1].content
    
    return "I apologize, but I couldn't generate a response. Please try again."
