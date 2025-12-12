import streamlit as st
import requests
from agno.agent import Agent
from agno.tools.firecrawl import FirecrawlTools
from agno.models.openai import OpenAIChat
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import List
from composio_phidata import Action, ComposioToolSet
import json
import os
import pandas as pd
from dotenv import load_dotenv, set_key
import pathlib

# Get the absolute path to the .env file
env_path = pathlib.Path(os.path.join(os.getcwd(), '.env'))

# Load environment variables from .env file
load_dotenv(dotenv_path=env_path)

class QuoraUserInteractionSchema(BaseModel):
    username: str = Field(description="The username of the user who posted the question or answer")
    bio: str = Field(description="The bio or description of the user")
    post_type: str = Field(description="The type of post, either 'question' or 'answer'")
    timestamp: str = Field(description="When the question or answer was posted")
    upvotes: int = Field(default=0, description="Number of upvotes received")
    links: List[str] = Field(default_factory=list, description="Any links included in the post")

class QuoraPageSchema(BaseModel):
    interactions: List[QuoraUserInteractionSchema] = Field(description="List of all user interactions (questions and answers) on the page")

def search_for_urls(company_description: str, firecrawl_api_key: str, num_links: int) -> List[str]:
    url = "https://api.firecrawl.dev/v1/search"
    headers = {
        "Authorization": f"Bearer {firecrawl_api_key}",
        "Content-Type": "application/json"
    }
    query1 = f"quora websites where people are looking for {company_description} services"
    payload = {
        "query": query1,
        "limit": num_links,
        "lang": "en",
        "location": "United States",
        "timeout": 60000,
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            results = data.get("data", [])
            return [result["url"] for result in results]
    return []

def extract_user_info_from_urls(urls: List[str], firecrawl_api_key: str) -> List[dict]:
    user_info_list = []
    firecrawl_app = FirecrawlApp(api_key=firecrawl_api_key)
    
    try:
        for url in urls:
            st.write(f"🔍 Extracting from: {url}")
            response = firecrawl_app.extract(
                urls=[url],
                prompt="""
                Extract information about all users who have posted questions or answers on this Quora page.
                For each user, extract their username, bio, the type of post (question or answer), 
                when it was posted, number of upvotes, and any links they included.
                """,
                schema=QuoraPageSchema.model_json_schema()
            )
            
            # Check if response is object or dict
            if hasattr(response, 'success'):
                success = response.success
                data = response.data
            else:
                success = response.get('success')
                data = response.get('data', response)

            if success or data:
                extracted_data = data
                # st.write(f"Debug Raw Data: {str(extracted_data)[:500]}") # Uncomment if needed
                if 'interactions' in extracted_data:
                    count = len(extracted_data['interactions'])
                    st.write(f"✅ Found {count} interactions")
                    for interaction in extracted_data['interactions']:
                        user_info = {
                            'url': url,
                            'username': interaction.get('username', 'Unknown'),
                            'bio': interaction.get('bio', 'No bio available'),
                            'post_type': interaction.get('post_type', 'Unknown'),
                            'timestamp': interaction.get('timestamp', 'Unknown'),
                            'upvotes': interaction.get('upvotes', 0),
                            'links': interaction.get('links', [])
                        }
                        user_info_list.append(user_info)
    except Exception as e:
        st.error(f"Error extracting user info: {str(e)}")
    
    return user_info_list

def format_user_info_to_flattened_json(user_info_list: List[dict]) -> List[dict]:
    flattened_data = []
    
    for user_info in user_info_list:
        flattened_user = {
            'url': user_info.get('url', ''),
            'username': user_info.get('username', ''),
            'bio': user_info.get('bio', ''),
            'post_type': user_info.get('post_type', ''),
            'timestamp': user_info.get('timestamp', ''),
            'upvotes': user_info.get('upvotes', 0),
            'links': ', '.join(user_info.get('links', [])),
        }
        flattened_data.append(flattened_user)
    
    return flattened_data

def create_google_sheets_agent(composio_api_key: str, openai_api_key: str) -> Agent:
    composio_tools = ComposioToolSet(
        api_key=composio_api_key,
        actions=[Action.GOOGLE_SHEETS_CREATE]
    )
    
    base_url = None
    if openai_api_key.startswith("sk-or-"):
        base_url = "https://openrouter.ai/api/v1"
    
    return Agent(
        model=OpenAIChat(id="deepseek/deepseek-chat", api_key=openai_api_key, base_url=base_url, max_tokens=1024),
        tools=[composio_tools],
        markdown=True
    )

def write_to_google_sheets(flattened_data: List[dict], composio_api_key: str, openai_api_key: str) -> str:
    if not flattened_data:
        return ""
    
    agent = create_google_sheets_agent(composio_api_key, openai_api_key)
    
    json_data = json.dumps(flattened_data, indent=2)
    
    response = agent.run(
        f"""Create a Google Sheet with the following data:
        {json_data}
        
        Format it nicely with appropriate column headers and return the link to the sheet.
        """
    )
    
    # Extract the Google Sheets link from the response
    content = response.content
    if "https://docs.google.com/spreadsheets" in content:
        for line in content.split('\n'):
            if "https://docs.google.com/spreadsheets" in line:
                return line.strip()
    
    return ""

def create_prompt_transformation_agent(openai_api_key: str) -> Agent:
    base_url = None
    if openai_api_key.startswith("sk-or-"):
        base_url = "https://openrouter.ai/api/v1"
        
    return Agent(
        model=OpenAIChat(id="deepseek/deepseek-chat", api_key=openai_api_key, base_url=base_url, max_tokens=1024),
        description="You are an expert at transforming verbose product/service descriptions into concise, targeted phrases for search queries.",
        instructions=[
            "Your task is to take a detailed description and extract the core product or service being offered, condensing it into 3-4 words.",
            "Examples:",
            "Input: 'We're looking for businesses that need help with their social media marketing, especially those struggling with content creation and engagement'",
            "Output: 'social media marketing'",
            "Input: 'Need to find businesses interested in implementing machine learning solutions for fraud detection'",
            "Output: 'ML fraud detection'",
            "Always focus on the core product/service and keep it concise but clear."
        ],
        markdown=True
    )

# Function to save API keys to .env file
def save_api_keys_to_env():
    try:
        # Save OpenAI API key
        if st.session_state.openai_api_key:
            set_key(env_path, "OPENAI_API_KEY", st.session_state.openai_api_key)
            
        # Save Firecrawl API key
        if st.session_state.firecrawl_api_key:
            set_key(env_path, "FIRECRAWL_API_KEY", st.session_state.firecrawl_api_key)
            
        # Save Composio API key
        if st.session_state.composio_api_key:
            set_key(env_path, "COMPOSIO_API_KEY", st.session_state.composio_api_key)
            
        # Update environment variables in session state
        st.session_state.env_openai_api_key = st.session_state.openai_api_key
        st.session_state.env_firecrawl_api_key = st.session_state.firecrawl_api_key
        st.session_state.env_composio_api_key = st.session_state.composio_api_key
        
        return True
    except Exception as e:
        st.error(f"Error saving API keys to .env file: {str(e)}")
        return False

def main():
    st.set_page_config(page_title="Lead Finder", layout="wide")
    st.title("🎯 Lead Finder")
    st.info("Powered by Firecrawl & Composio. Find leads on Quora and export to Sheets.")

    # Initialize session state for API keys if not already set
    if "api_keys_initialized" not in st.session_state:
        # Get API keys from environment variables
        st.session_state.env_openai_api_key = os.getenv("OPENAI_API_KEY", "")
        st.session_state.env_firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY", "")
        st.session_state.env_composio_api_key = os.getenv("COMPOSIO_API_KEY", "")
        
        # Initialize the working API keys with environment values
        st.session_state.openai_api_key = st.session_state.env_openai_api_key
        st.session_state.firecrawl_api_key = st.session_state.env_firecrawl_api_key
        st.session_state.composio_api_key = st.session_state.env_composio_api_key
        
        st.session_state.api_keys_initialized = True

    with st.sidebar:
        st.header("API Keys")
        
        # API Key Management Section
        with st.expander("Configure API Keys", expanded=False):
            st.info("API keys from .env file are used by default. You can override them here.")
            
            # Function to handle API key updates
            def update_api_key(key_name, env_key_name, help_text=""):
                new_value = st.text_input(
                    f"{key_name}", 
                    value=st.session_state[env_key_name] if st.session_state[env_key_name] else "",
                    type="password",
                    help=help_text
                )
                
                # Only update if user entered something or if we have an env value
                if new_value:
                    st.session_state[key_name.lower()] = new_value
                    return True
                elif st.session_state[env_key_name]:
                    st.session_state[key_name.lower()] = st.session_state[env_key_name]
                    return True
                return False
            
            # API keys inputs
            has_firecrawl = update_api_key(
                "Firecrawl API Key", 
                "env_firecrawl_api_key", 
                help_text="Get your Firecrawl API key from [Firecrawl's website](https://www.firecrawl.dev/app/api-keys)"
            )
            
            has_openai = update_api_key(
                "OpenAI API Key", 
                "env_openai_api_key", 
                help_text="Get your OpenAI API key from [OpenAI's website](https://platform.openai.com/api-keys)"
            )
            
            has_composio = update_api_key(
                "Composio API Key", 
                "env_composio_api_key", 
                help_text="Get your Composio API key from [Composio's website](https://composio.ai)"
            )
            
            # Buttons for API key management
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Reset to .env values"):
                    st.session_state.openai_api_key = st.session_state.env_openai_api_key
                    st.session_state.firecrawl_api_key = st.session_state.env_firecrawl_api_key
                    st.session_state.composio_api_key = st.session_state.env_composio_api_key
                    st.experimental_rerun()
            
            with col2:
                if st.button("Save to .env file"):
                    if save_api_keys_to_env():
                        st.success("API keys saved to .env file!")
                        st.experimental_rerun()
        
        # Display API status
        api_status_ok = has_openai and has_firecrawl and has_composio
        
        if api_status_ok:
            st.success("✅ All required API keys are configured")
        else:
            missing_keys = []
            if not has_openai:
                missing_keys.append("OpenAI API Key")
            if not has_firecrawl:
                missing_keys.append("Firecrawl API Key")
            if not has_composio:
                missing_keys.append("Composio API Key")
            
            st.error(f"❌ Missing API keys: {', '.join(missing_keys)}")
        
        # Search settings
        st.subheader("Search Settings")
        num_links = st.number_input("Number of links to search", min_value=1, max_value=10, value=3)
        
        if st.button("Reset Session"):
            # Keep API keys but clear other session state
            api_keys = {
                "api_keys_initialized": st.session_state.api_keys_initialized,
                "env_openai_api_key": st.session_state.env_openai_api_key,
                "env_firecrawl_api_key": st.session_state.env_firecrawl_api_key,
                "env_composio_api_key": st.session_state.env_composio_api_key,
                "openai_api_key": st.session_state.openai_api_key,
                "firecrawl_api_key": st.session_state.firecrawl_api_key,
                "composio_api_key": st.session_state.composio_api_key
            }
            st.session_state.clear()
            for key, value in api_keys.items():
                st.session_state[key] = value
            st.experimental_rerun()

    user_query = st.text_area(
        "Describe what kind of leads you're looking for:",
        placeholder="e.g., Looking for users who need automated video editing software with AI capabilities",
        help="Be specific about the product/service and target audience. The AI will convert this into a focused search query."
    )

    if st.button("Generate Leads"):
        if not api_status_ok:
            st.error("Please configure all required API keys in the sidebar.")
        elif not user_query:
            st.error("Please describe what leads you're looking for.")
        else:
            with st.spinner("Processing your query..."):
                try:
                    transform_agent = create_prompt_transformation_agent(st.session_state.openai_api_key)
                    company_description_response = transform_agent.run(f"Transform this query into a concise 3-4 word company description: {user_query}")
                    company_description = company_description_response.content
                except Exception as e:
                    st.warning(f"AI transformation failed ({str(e)}), using raw query.")
                    company_description = user_query
                
                st.write("🎯 Searching for:", company_description)
            
            with st.spinner("Searching for relevant URLs..."):
                urls = search_for_urls(company_description, st.session_state.firecrawl_api_key, num_links)
            
            if urls:
                st.subheader("Quora Links Used:")
                for url in urls:
                    st.write(url)
                
                with st.spinner("Extracting user info from URLs..."):
                    user_info_list = extract_user_info_from_urls(urls, st.session_state.firecrawl_api_key)
                
                with st.spinner("Formatting user info..."):
                    flattened_data = format_user_info_to_flattened_json(user_info_list)
                    
                    # Create DataFrame and CSV for download
                    if flattened_data:
                        df = pd.DataFrame(flattened_data)
                    else:
                        # Create empty DataFrame with expected columns
                        columns = ['url', 'username', 'bio', 'post_type', 'timestamp', 'upvotes', 'links']
                        df = pd.DataFrame(columns=columns)
                        
                    csv = df.to_csv(index=False).encode('utf-8')
                    
                    st.success(f"✅ Extracted {len(flattened_data)} leads!")
                    st.write("Leads found: ", len(flattened_data))
                    
                    st.download_button(
                        label="📥 Download Leads as CSV",
                        data=csv,
                        file_name="quora_leads.csv",
                        mime="text/csv",
                    )
                
                with st.spinner("Writing to Google Sheets..."):
                    try:
                        google_sheets_link = write_to_google_sheets(flattened_data, st.session_state.composio_api_key, st.session_state.openai_api_key)
                        if google_sheets_link:
                            st.subheader("Google Sheets Link:")
                            st.markdown(f"[View Google Sheet]({google_sheets_link})")
                        else:
                            st.info("Could not generate Google Sheet link automatically. Please use the CSV download above.")
                    except Exception as e:
                        st.warning(f"Skipping Google Sheets export due to error: {e}")
                        st.info("Please use the CSV download button above.")
            else:
                st.warning("No relevant URLs found.")

if __name__ == "__main__":
    main()
