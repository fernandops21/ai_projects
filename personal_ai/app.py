import os
import subprocess
import gradio as gr
import datetime
import uuid
import time
import nltk

# Create required directories
os.makedirs("data", exist_ok=True)

# Set up NLTK resources path and download required data
def setup_nltk():
    """Set up NLTK resources needed by the application."""
    print("Setting up NLTK resources...")
    
    # Create a directory for NLTK data in the project folder
    nltk_data_dir = os.path.join(os.getcwd(), "nltk_data")
    os.makedirs(nltk_data_dir, exist_ok=True)
    
    # Tell NLTK to use this directory
    nltk.data.path.append(nltk_data_dir)
    
    # Newer NLTK versions (>=3.8.2) need punkt_tab instead of punkt
    for resource in ("punkt", "punkt_tab"):
        try:
            nltk.data.find(f"tokenizers/{resource}")
            print(f"NLTK {resource} tokenizer already available.")
        except LookupError:
            print(f"Downloading {resource} tokenizer...")
            nltk.download(resource, download_dir=nltk_data_dir)
    print("NLTK resources ready.")

# Run NLTK setup before importing our modules
# This ensures resources are available when they're needed
setup_nltk()


from memory.working import WorkingMemory
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory
from memory.procedural import ProceduralMemory
from utils.extraction import InformationExtractor
from utils.prompting import PromptBuilder

class PersonalAI:
    """
    A personal AI assistant that learns about the user through interactions.
    Integrates multiple memory systems to provide personalized responses.
    """
    
    def __init__(self, model_name="mistral:7b"):
        """Initialize the personal AI system."""
        
        # Initialize memory systems
        print("Initializing memory systems...")
        self.working_memory = WorkingMemory(max_turns=10)
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = SemanticMemory()
        self.procedural_memory = ProceduralMemory()
        
        # Initialize utilities
        self.extractor = InformationExtractor()
        self.prompt_builder = PromptBuilder(
            self.working_memory,
            self.semantic_memory,
            self.episodic_memory,
            self.procedural_memory
        )
        
        # Set AI model
        self.model_name = model_name
        
        print("Personal AI system initialized.")
    
    def process_message(self, message, history):
        """
        Process a user message and generate a response.
        
        Args:
            message: The user's message
            history: Conversation history from the UI
            
        Returns:
            The AI's response
        """
        # Record interaction time
        self.procedural_memory.record_interaction_time()
        
        # Extract information from the message
        extracted_info = self.extractor.extract_all(message)
        
        # Update semantic memory with extracted information
        for item, sentiment in extracted_info["preferences"]:
            self.semantic_memory.add_preference(item, sentiment)
        
        for trait in extracted_info["traits"]:
            self.semantic_memory.add_trait(trait, "yes")
        
        for skill in extracted_info["skills"]:
            self.semantic_memory.add_skill(skill)
        
        for key, value in extracted_info["demographics"].items():
            self.semantic_memory.add_demographic(key, value)
        
        for goal in extracted_info["goals"]:
            self.semantic_memory.add_goal(goal)
        
        # Extract topics and update procedural memory
        topics = self.extractor.extract_topics(message)
        for topic in topics:
            self.procedural_memory.record_topic(topic)
        
        # Build the prompt using all memory systems
        prompt = self.prompt_builder.build_prompt(message)
        
        # Generate response using local model
        try:
            print(f"Sending prompt to model... (length: {len(prompt)} chars)")
            start_time = time.time()
            
            # Call the local Ollama model
            result = subprocess.run(
                ["ollama", "run", self.model_name, prompt],
                capture_output=True,
                text=True,
                timeout=60  # Set a timeout to prevent hanging
            )
            
            response_time = time.time() - start_time
            print(f"Model responded in {response_time:.2f} seconds")
            
            response = result.stdout.strip()
            
            # Update working memory with this exchange
            self.working_memory.add_exchange(message, response)
            
            # Store this interaction in episodic memory
            # Rate importance based on message length and complexity
            importance = min(5.0, 1.0 + (len(message) / 100))
            self.episodic_memory.add_episode(
                f"User: {message}\nAI: {response}",
                importance=importance
            )
            
            # Add any clearly stated facts about the user to semantic memory
            # This is a simplified approach - a real system would use more sophisticated NLP
            if "I am" in message or "I'm" in message:
                self.semantic_memory.add_knowledge(message)
            
            return response
            
        except subprocess.TimeoutExpired:
            return "I'm taking longer than expected to think about this. This might happen with complex questions on systems with limited resources."
            
        except Exception as e:
            return f"I encountered an error while processing your message: {str(e)}"

# Create the Gradio interface
def create_app():
    """Create and configure the Gradio web interface."""
    personal_ai = PersonalAI()
    
    # Create interface
    demo = gr.ChatInterface(
        fn=personal_ai.process_message,
        title="Your Personal AI Assistant",
        description=(
            "This AI learns about you over time to provide increasingly personalized responses. "
            "It remembers your preferences, past conversations, and adapts to your interaction style. "
            "All data stays on your local machine for privacy."
        ),
        examples=[
            "Hi there! My name is Fernando and I work as a data scientist.",
            "I really enjoy playing volleyball, boardgames and watching movies on the weekend.",
            "I'm trying to learn more about machine learning and AI.",
            "I prefer detailed technical explanations over simplified ones.",
            "Could you help me plan a vacation to Japan next summer?"
        ],
        theme="soft"
    )
    
    return demo

# Run the application
if __name__ == "__main__":
    print("Starting Personal AI Assistant...")
    print("This system learns from your interactions and stores all data locally.")
    print("Memory systems: Working, Episodic, Semantic, and Procedural")
    app = create_app()
    app.launch()