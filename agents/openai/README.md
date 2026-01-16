# OpenAI Agents SDK Research Application

This application demonstrates the use of the OpenAI Agents SDK to create a research assistant that can search the web and a personal knowledge base.

## Features

- Web search capabilities using OpenAI's WebSearchTool
- File search in a personal knowledge base using vector search
- Orchestration between different specialized agents
- Trace viewing for debugging and understanding agent behavior
- Streamlit UI for easy interaction

## Requirements

- Python 3.9+
- OpenAI API key with access to the Agents SDK
- Required packages (see requirements.txt)

## Installation

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY='your-api-key'
```

## Usage

Run the Streamlit application:

```bash
streamlit run agents/openai/basic-agent.py
```

The application will open in your browser, where you can:

1. Enter your OpenAI API key if not set as an environment variable
2. Select a model to use (gpt-4o-mini or gpt-4o)
3. Choose between web search, file search, or combined research
4. Upload files to your knowledge base
5. Query your knowledge base
6. View traces of agent runs for debugging

## How It Works

The application uses three main agents:

1. **Research Agent**: Uses web search to find information on the internet
2. **File Search Agent**: Searches through your personal knowledge base
3. **Orchestrator Agent**: Coordinates between web search and file search based on the query

Files uploaded to the knowledge base are stored in a vector store for semantic search.

## Troubleshooting

- If you encounter errors related to the OpenAI API, check that your API key is valid and has access to the Agents SDK
- If file search is not working, ensure that your vector store is properly set up
- For other issues, check the trace viewer for detailed debugging information

## License

This project is licensed under the MIT License - see the LICENSE file for details. 