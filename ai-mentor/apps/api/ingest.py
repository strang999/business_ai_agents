"""
ingest.py - Knowledge Base Ingestion Script for AI Life Coach

USAGE:
1. Place your PDF, TXT, or MD files in the ./documents folder
2. Set environment variables: SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY
3. Run: python ingest.py

This script will:
- Load all documents from ./documents (including subdirectories)
- Extract text from PDFs
- Split them into semantic chunks
- Generate embeddings via OpenAI
- Upload to Supabase pgvector with course metadata
"""

import os
import glob
import re
from pathlib import Path
from typing import List
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from supabase import create_client, Client

load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DOCUMENTS_DIR = "./documents"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


# Course folder to metadata mapping
COURSE_METADATA = {
    "self made man": {
        "course": "SelfMade Man",
        "driver_target": "all",
        "concept": "theory"
    },
    "relationships": {
        "course": "Love & Relationships",
        "driver_target": "please_others",  # Most relevant
        "concept": "practice"
    },
    "checkup of your life": {
        "course": "Life Checkup",
        "driver_target": "all",
        "concept": "diagnostic"
    },
    "o_chem_signalit_telo": {
        "course": "Body Signals",
        "driver_target": "all",
        "concept": "tool"
    }
}

# Session number extraction patterns
SESSION_PATTERN = re.compile(r'Session[_\s.]?(\d+)', re.IGNORECASE)


def get_supabase_client() -> Client:
    """Initialize Supabase client."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def extract_session_number(filename: str) -> int:
    """Extract session number from filename."""
    match = SESSION_PATTERN.search(filename)
    if match:
        return int(match.group(1))
    return 0  # Default for non-session files


def get_folder_metadata(folder_path: str) -> dict:
    """Get metadata based on folder name."""
    folder_name = Path(folder_path).name.lower()
    for key, metadata in COURSE_METADATA.items():
        if key in folder_name:
            return metadata
    return {"course": "Unknown", "driver_target": "all", "concept": "theory"}


def load_documents(directory: str) -> List[dict]:
    """Load all documents from directory and subdirectories."""
    documents = []
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_lower = file.lower()
            
            try:
                # Load based on file type
                if file_lower.endswith('.pdf'):
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                elif file_lower.endswith(('.txt', '.md')):
                    loader = TextLoader(file_path, encoding="utf-8")
                    docs = loader.load()
                else:
                    continue  # Skip unsupported files
                
                # Enrich with metadata
                folder_meta = get_folder_metadata(root)
                session_num = extract_session_number(file)
                
                for doc in docs:
                    doc.metadata.update({
                        "source": file,
                        "course": folder_meta["course"],
                        "driver_target": folder_meta["driver_target"],
                        "concept": folder_meta["concept"],
                        "session_number": session_num,
                        "folder": Path(root).name
                    })
                
                documents.extend(docs)
                print(f"✓ Loaded: {file} ({len(docs)} pages)")
                
            except Exception as e:
                print(f"✗ Error loading {file}: {e}")
    
    print(f"\nTotal documents loaded: {len(documents)}")
    return documents


def split_documents(documents: List) -> List:
    """Split documents into chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    return chunks


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using OpenAI."""
    embeddings_model = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=OPENAI_API_KEY
    )
    
    # Process in batches to avoid rate limits
    batch_size = 100
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = embeddings_model.embed_documents(batch)
        all_embeddings.extend(embeddings)
        print(f"Generated embeddings for batch {i // batch_size + 1}")
    
    print(f"Total embeddings generated: {len(all_embeddings)}")
    return all_embeddings


def upload_to_supabase(supabase: Client, chunks: List, embeddings: List[List[float]]):
    """Upload chunks with embeddings to Supabase (Enhanced schema)."""
    records = []
    for chunk, embedding in zip(chunks, embeddings):
        meta = chunk.metadata
        record = {
            "content": chunk.page_content,
            "embedding": embedding,
            "source": meta.get("source", "unknown"),
            "user_id": None,  # Global knowledge
            "concept": meta.get("concept", "theory"),
            "session_number": meta.get("session_number", 0),
            "driver_target": meta.get("driver_target", "all"),
            "metadata": {
                "course": meta.get("course"),
                "folder": meta.get("folder"),
                "page": meta.get("page", 0)
            }
        }
        records.append(record)
    
    # Batch insert
    batch_size = 50
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        try:
            supabase.table("memories").insert(batch).execute()
            print(f"✓ Uploaded batch {i // batch_size + 1}/{(len(records) // batch_size) + 1}")
        except Exception as e:
            print(f"✗ Error uploading batch: {e}")
    
    print(f"✓ Total {len(records)} records uploaded to Supabase")


def main():
    print("=" * 50)
    print("AI Life Coach - Knowledge Ingestion")
    print("Pavel Bilskiy Methodology")
    print("=" * 50)
    
    # Validate environment
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY must be set for embeddings")
    
    # Create documents directory if not exists
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    
    # Load documents
    documents = load_documents(DOCUMENTS_DIR)
    if not documents:
        print(f"No documents found in {DOCUMENTS_DIR}")
        return
    
    # Split into chunks
    chunks = split_documents(documents)
    
    # Generate embeddings
    texts = [chunk.page_content for chunk in chunks]
    embeddings = generate_embeddings(texts)
    
    # Upload to Supabase
    supabase = get_supabase_client()
    upload_to_supabase(supabase, chunks, embeddings)
    
    print("=" * 50)
    print("Ingestion complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
