#!/usr/bin/env python3
"""
Quick launcher for Trading Agent
"""

import os
import sys
import subprocess
from pathlib import Path


def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        print("⚠️  .env file not found!")
        print("📝 Creating .env from template...")
        
        if env_example.exists():
            env_example.read_text()
            with open(".env", "w") as f:
                f.write(env_example.read_text())
            
            print("✅ Created .env file")
            print("\n🔑 Please add your OpenRouter API key to .env:")
            print("   OPENAI_API_KEY=sk-or-v1-your-key-here\n")
            
            choice = input("Continue anyway? (y/n): ")
            if choice.lower() != 'y':
                sys.exit(0)
        else:
            print("❌ .env.example not found!")
            sys.exit(1)
    else:
        print("✅ .env file found")


def check_dependencies():
    """Check if dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    try:
        import streamlit
        import langchain
        import langgraph
        from dotenv import load_dotenv
        print("✅ All core dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n📥 Installing dependencies...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False


def launch_app():
    """Launch the Streamlit app"""
    print("\n🚀 Launching Trading Agent...")
    print("=" * 60)
    print("📈 Trading Prediction Agent")
    print("🌐 Opening in browser...")
    print("=" * 60)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Error launching app: {e}")
        sys.exit(1)


def main():
    """Main launcher"""
    print("=" * 60)
    print("🤖 Trading Agent Launcher")
    print("=" * 60)
    
    # Check environment
    check_env_file()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install dependencies manually:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Launch app
    launch_app()


if __name__ == "__main__":
    main()
