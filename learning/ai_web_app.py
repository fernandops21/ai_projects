import gradio as gr
import subprocess
import time

def chat_with_model(message, history):
    """
    Function that processes messages and returns AI responses.
    
    Args:
        message: The current message from the user
        history: A list of previous [user_message, bot_message] pairs
    
    Returns:
        AI's response to the current message
    """
    # Format the conversation history and current message for context
    formatted_prompt = ""
    
    # Add conversation history for context if it exists
    if history:
        for human_msg, ai_msg in history:
            formatted_prompt += f"Human: {human_msg}\nAssistant: {ai_msg}\n\n"
    
    # Add the current message
    formatted_prompt += f"Human: {message}\nAssistant:"
    
    # Call the local Ollama model
    try:
        # Print to console for debugging
        print(f"Sending prompt to model: {message[:50]}...")
        
        # Start timing the response
        start_time = time.time()
        
        # Run the model with the formatted prompt
        result = subprocess.run(
            ["ollama", "run", "mistral:7b", formatted_prompt],
            capture_output=True,
            text=True,
            timeout=60  # Set a timeout to prevent hanging
        )
        
        # Calculate response time
        elapsed_time = time.time() - start_time
        print(f"Model responded in {elapsed_time:.2f} seconds")
        
        # Get the model's response
        response = result.stdout.strip()
        
        return response
    
    except subprocess.TimeoutExpired:
        return "The model took too long to respond. This might happen with complex questions on slower hardware."
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Create the Gradio interface
demo = gr.ChatInterface(
    fn=chat_with_model,
    title="Your Personal AI Assistant (Running Locally)",
    description="Chat with a Mistral-7B model running entirely on your computer. Your data never leaves your machine.",
    examples=["What is machine learning?", 
              "Write a short poem about technology",
              "Explain quantum computing to a 10-year old"],
    theme="soft"
)

# Run the web interface
if __name__ == "__main__":
    print("Starting the web interface...")
    print("Once loaded, open the URL shown below in your web browser")
    demo.launch(share=False)  # Set share=True if you want a public link (not recommended for privacy)