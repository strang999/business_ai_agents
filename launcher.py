import os
import sys
import subprocess
import inquirer

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_streamlit(script_path):
    print(f"🚀 Launching {script_path}...")
    subprocess.run(["streamlit", "run", script_path], check=True)

def run_python(script_path):
    print(f"🚀 Running {script_path}...")
    subprocess.run([sys.executable, script_path], check=True)

def main():
    while True:
        clear_screen()
        print("="*50)
        print("   🚀 BUSINESS AI SOLUTIONS SUITE")
        print("="*50)
        
        questions = [
            inquirer.List('agent',
                          message="Select an agent to launch",
                          choices=[
                              '🎯 Lead Finder (Streamlit)',
                              '🏠 Real Estate Assistant (WhatsApp CLI)',
                              '🏠 Real Estate Dashboard (Streamlit)',
                              '📅 Content Calendar Creator (Streamlit)',
                              '📞 Sales Qualifier (CLI)',
                              '🚀 Startup Validator (CrewAI Streamlit)',
                              '🧠 Deep Research Agent (LangGraph Streamlit)',
                              'Exit'
                          ],
            ),
        ]
        
        try:
            answers = inquirer.prompt(questions)
            if not answers:
                break
                
            choice = answers['agent']
            
            if choice == 'Exit':
                print("Goodbye! 👋")
                break
                
            elif choice == '🎯 Lead Finder (Streamlit)':
                run_streamlit(os.path.join("lead_gen", "app.py"))
                
            elif choice == '🏠 Real Estate Assistant (WhatsApp CLI)':
                run_python(os.path.join("real_estate", "bot.py"))
                input("\nPress Enter to continue...")
                
            elif choice == '🏠 Real Estate Dashboard (Streamlit)':
                run_streamlit(os.path.join("real_estate", "agent.py"))
                
            elif choice == '📅 Content Calendar Creator (Streamlit)':
                run_streamlit(os.path.join("social_media", "app.py"))
                
            elif choice == '📞 Sales Qualifier (CLI)':
                run_python(os.path.join("sales_qualifier", "agent.py"))
                input("\nPress Enter to continue...")
                
            elif choice == '🚀 Startup Validator (CrewAI Streamlit)':
                run_streamlit(os.path.join("startup_validator", "app.py"))
                
            elif choice == '🧠 Deep Research Agent (LangGraph Streamlit)':
                run_streamlit(os.path.join("deep_research", "app.py"))
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    # Check if inquirer is installed
    try:
        import inquirer
    except ImportError:
        print("Installing required package 'inquirer'...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "inquirer"])
        import inquirer
        
    main()
