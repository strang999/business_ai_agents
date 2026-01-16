import streamlit as st
from openai import OpenAI
from mem0 import Memory
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key
import pathlib

# Get the absolute path to the .env file
env_path = pathlib.Path(os.path.join(os.getcwd(), '.env'))

# Load environment variables from .env file
load_dotenv(dotenv_path=env_path)

# Set up the Streamlit App
st.set_page_config(page_title="AI Customer Support Agent", layout="wide")
st.title("AI Customer Support Agent with Memory 🛒")
st.caption("Chat with a customer support assistant who remembers your past interactions.")

# Initialize session state for API keys if not already set
if "api_keys_initialized" not in st.session_state:
    # Get API keys from environment variables
    st.session_state.env_openai_api_key = os.getenv("OPENAI_API_KEY", "")
    st.session_state.env_qdrant_url = os.getenv("QDRANT_URL", "localhost")
    st.session_state.env_qdrant_port = os.getenv("QDRANT_PORT", "6333")
    st.session_state.env_openai_model = os.getenv("OPENAI_MODEL_ID", "gpt-4")
    
    # Initialize the working API keys with environment values
    st.session_state.openai_api_key = st.session_state.env_openai_api_key
    st.session_state.qdrant_url = st.session_state.env_qdrant_url
    st.session_state.qdrant_port = st.session_state.env_qdrant_port
    st.session_state.openai_model = st.session_state.env_openai_model
    
    st.session_state.api_keys_initialized = True

# Function to save API keys to .env file
def save_api_keys_to_env():
    try:
        # Save OpenAI API key
        if st.session_state.openai_api_key:
            set_key(env_path, "OPENAI_API_KEY", st.session_state.openai_api_key)
            
        # Save Qdrant URL and port
        if st.session_state.qdrant_url:
            set_key(env_path, "QDRANT_URL", st.session_state.qdrant_url)
        
        if st.session_state.qdrant_port:
            set_key(env_path, "QDRANT_PORT", st.session_state.qdrant_port)
            
        # Save OpenAI model
        if st.session_state.openai_model:
            set_key(env_path, "OPENAI_MODEL_ID", st.session_state.openai_model)
            
        # Update environment variables in session state
        st.session_state.env_openai_api_key = st.session_state.openai_api_key
        st.session_state.env_qdrant_url = st.session_state.qdrant_url
        st.session_state.env_qdrant_port = st.session_state.qdrant_port
        st.session_state.env_openai_model = st.session_state.openai_model
        
        return True
    except Exception as e:
        st.error(f"Error saving API keys to .env file: {str(e)}")
        return False

# Sidebar for API key management
with st.sidebar:
    st.title("Configuration")
    
    # API Key Management Section
    with st.expander("API Key Management", expanded=False):
        st.info("API keys from .env file are used by default. You can override them here.")
        
        # Function to handle API key updates
        def update_api_key(key_name, env_key_name, password=True, help_text=""):
            input_type = "password" if password else "default"
            new_value = st.text_input(
                f"{key_name}", 
                value=st.session_state[env_key_name] if st.session_state[env_key_name] else "",
                type=input_type,
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
        has_openai = update_api_key(
            "OpenAI API Key", 
            "env_openai_api_key", 
            password=True,
            help_text="Enter your OpenAI API key"
        )
        
        # OpenAI model selection
        openai_models = ["gpt-4", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        selected_model = st.selectbox(
            "OpenAI Model",
            options=openai_models,
            index=openai_models.index(st.session_state.openai_model) if st.session_state.openai_model in openai_models else 0,
            help="Select the OpenAI model to use"
        )
        st.session_state.openai_model = selected_model
        has_model = True
        
        # Qdrant configuration
        st.subheader("Qdrant Vector Store Settings")
        has_qdrant_url = update_api_key(
            "Qdrant Host", 
            "env_qdrant_url", 
            password=False,
            help_text="Enter your Qdrant host (default: localhost)"
        )
        
        has_qdrant_port = update_api_key(
            "Qdrant Port", 
            "env_qdrant_port", 
            password=False,
            help_text="Enter your Qdrant port (default: 6333)"
        )
        
        # Buttons for API key management
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Reset to .env values"):
                st.session_state.openai_api_key = st.session_state.env_openai_api_key
                st.session_state.qdrant_url = st.session_state.env_qdrant_url
                st.session_state.qdrant_port = st.session_state.env_qdrant_port
                st.session_state.openai_model = st.session_state.env_openai_model
                st.experimental_rerun()
        
        with col2:
            if st.button("Save to .env file"):
                if save_api_keys_to_env():
                    st.success("Configuration saved to .env file!")
                    st.experimental_rerun()
    
    # Display API status
    api_status_ok = has_openai and has_qdrant_url and has_qdrant_port and has_model
    
    if api_status_ok:
        st.success("✅ All required configurations are set")
    else:
        missing_keys = []
        if not has_openai:
            missing_keys.append("OpenAI API Key")
        if not has_qdrant_url:
            missing_keys.append("Qdrant Host")
        if not has_qdrant_port:
            missing_keys.append("Qdrant Port")
        
        st.error(f"❌ Missing configuration: {', '.join(missing_keys)}")
    
    # Separator
    st.markdown("---")
    
    # Customer Management Section
    st.subheader("Customer Management")
    previous_customer_id = st.session_state.get("previous_customer_id", None)
    customer_id = st.text_input("Enter Customer ID")

    if customer_id != previous_customer_id:
        st.session_state.messages = []
        st.session_state.previous_customer_id = customer_id
        st.session_state.customer_data = None

    # Customer data management buttons
    if customer_id:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate Data"):
                if api_status_ok:
                    with st.spinner("Generating customer data..."):
                        # Initialize the agent here to ensure we're using the latest config
                        if 'support_agent' in locals():
                            st.session_state.customer_data = support_agent.generate_synthetic_data(customer_id)
                        else:
                            st.error("Agent not initialized. Please check your configuration.")
                    if st.session_state.customer_data:
                        st.success("Data generated!")
                    else:
                        st.error("Failed to generate data.")
                else:
                    st.error("Configure API keys first.")
        
        with col2:
            if st.button("View Profile"):
                if st.session_state.get("customer_data"):
                    st.session_state.show_profile = True
                else:
                    st.info("Generate data first.")
    else:
        st.info("Enter a customer ID to manage customer data.")
    
    # Show customer profile if requested
    if st.session_state.get("show_profile", False) and st.session_state.get("customer_data"):
        with st.expander("Customer Profile", expanded=True):
            st.json(st.session_state.customer_data)
            if st.button("Hide Profile"):
                st.session_state.show_profile = False
                st.experimental_rerun()

# Define the CustomerSupportAIAgent class outside the conditional block
class CustomerSupportAIAgent:
    def __init__(self):
        # Check if API keys are configured
        if not st.session_state.get("openai_api_key"):
            st.error("OpenAI API key is not configured.")
            st.stop()
            
        # Set the OpenAI API key
        os.environ['OPENAI_API_KEY'] = st.session_state.openai_api_key
            
        # Initialize Mem0 with Qdrant as the vector store
        config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "host": st.session_state.qdrant_url,
                    "port": int(st.session_state.qdrant_port),
                }
            },
        }
        try:
            self.memory = Memory.from_config(config)
        except Exception as e:
            st.error(f"Failed to initialize memory: {e}")
            st.stop()  # Stop execution if memory initialization fails

        self.client = OpenAI()
        self.app_id = "customer-support"
        self.model = st.session_state.openai_model

    def handle_query(self, query, user_id=None):
        try:
            # Search for relevant memories
            relevant_memories = self.memory.search(query=query, user_id=user_id)
            
            # Build context from relevant memories
            context = "Relevant past information:\n"
            if relevant_memories and "results" in relevant_memories:
                for memory in relevant_memories["results"]:
                    if "memory" in memory:
                        context += f"- {memory['memory']}\n"

            # Generate a response using OpenAI
            full_prompt = f"{context}\nCustomer: {query}\nSupport Agent:"
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a customer support AI agent for TechGadgets.com, an online electronics store."},
                    {"role": "user", "content": full_prompt}
                ]
            )
            answer = response.choices[0].message.content

            # Add the query and answer to memory
            self.memory.add(query, user_id=user_id, metadata={"app_id": self.app_id, "role": "user"})
            self.memory.add(answer, user_id=user_id, metadata={"app_id": self.app_id, "role": "assistant"})

            return answer
        except Exception as e:
            st.error(f"An error occurred while handling the query: {e}")
            return "Sorry, I encountered an error. Please try again later."

    def get_memories(self, user_id=None):
        try:
            # Retrieve all memories for a user
            return self.memory.get_all(user_id=user_id)
        except Exception as e:
            st.error(f"Failed to retrieve memories: {e}")
            return None

    def generate_synthetic_data(self, user_id: str) -> dict | None:
        try:
            today = datetime.now()
            order_date = (today - timedelta(days=10)).strftime("%B %d, %Y")
            expected_delivery = (today + timedelta(days=2)).strftime("%B %d, %Y")

            prompt = f"""Generate a detailed customer profile and order history for a TechGadgets.com customer with ID {user_id}. Include:
            1. Customer name and basic info
            2. A recent order of a high-end electronic device (placed on {order_date}, to be delivered by {expected_delivery})
            3. Order details (product, price, order number)
            4. Customer's shipping address
            5. 2-3 previous orders from the past year
            6. 2-3 customer service interactions related to these orders
            7. Any preferences or patterns in their shopping behavior

            Format the output as a JSON object."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data generation AI that creates realistic customer profiles and order histories. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )

            customer_data = json.loads(response.choices[0].message.content)

            # Add generated data to memory
            for key, value in customer_data.items():
                if isinstance(value, list):
                    for item in value:
                        self.memory.add(
                            json.dumps(item), 
                            user_id=user_id, 
                            metadata={"app_id": self.app_id, "role": "system"}
                        )
                else:
                    self.memory.add(
                        f"{key}: {json.dumps(value)}", 
                        user_id=user_id, 
                        metadata={"app_id": self.app_id, "role": "system"}
                    )

            return customer_data
        except Exception as e:
            st.error(f"Failed to generate synthetic data: {e}")
            return None

# Main chat interface
if api_status_ok:
    # Initialize the CustomerSupportAIAgent
    support_agent = CustomerSupportAIAgent()
    
    if customer_id:
        # Memory viewer
        with st.expander("Memory Viewer", expanded=False):
            if st.button("View Memory"):
                memories = support_agent.get_memories(user_id=customer_id)
                if memories and "results" in memories and memories["results"]:
                    st.write(f"Memory for customer **{customer_id}**:")
                    for memory in memories["results"]:
                        if "memory" in memory:
                            st.write(f"- {memory['memory']}")
                else:
                    st.info("No memory found for this customer ID.")
        
        # Initialize the chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display the chat history
        st.subheader(f"Chat with Customer Support (ID: {customer_id})")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Accept user input
        query = st.chat_input("How can I assist you today?")

        if query:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.markdown(query)

            # Generate and display response
            with st.spinner("Generating response..."):
                answer = support_agent.handle_query(query, user_id=customer_id)

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.markdown(answer)
    else:
        st.info("👈 Please enter a customer ID in the sidebar to start chatting.")
else:
    st.warning("⚠️ Please configure your API keys in the sidebar to use the customer support agent.")