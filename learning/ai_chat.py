import subprocess
import sys

def chat_with_ai(prompt):
    """Send a prompt to the local Ollama model and return its response."""
    # Run the Ollama command and capture its output
    result = subprocess.run(
        ["ollama", "run", "mistral:7b", prompt],
        capture_output=True,
        text=True
    )
    
    # Return the model's response
    return result.stdout.strip()

# Main program logic
if __name__ == "__main__":
    print("Local AI Chat (using Mistral-7B model)")
    print("Type 'exit' to quit")
    print("-" * 40)
    
    # Check if we need to download the model first
    print("Checking if model is available...")
    subprocess.run(["ollama", "list"], capture_output=True)
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check if user wants to exit
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        
        # Get AI response
        print("\nThinking...")
        response = chat_with_ai(user_input)
        
        # Print response
        print("\nFernando's Personal AI: " + response)