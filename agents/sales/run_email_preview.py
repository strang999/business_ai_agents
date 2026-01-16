#!/usr/bin/env python3

import os
import sys
import subprocess

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

def main():
    """Run the email preview Streamlit application"""
    print("Starting Email Preview & Send application...")
    
    # Use the Streamlit CLI to run the app
    streamlit_cmd = ["streamlit", "run", os.path.join(current_dir, "email_preview.py")]
    
    try:
        # Run the Streamlit command
        subprocess.run(streamlit_cmd)
    except KeyboardInterrupt:
        print("\nApplication stopped.")
    except Exception as e:
        print(f"Error running Streamlit application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 