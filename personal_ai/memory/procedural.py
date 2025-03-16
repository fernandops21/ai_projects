import os
import json
import datetime

class ProceduralMemory:
    """
    Procedural memory stores information about how the user prefers
    to interact with the AI. This includes response style preferences,
    conversation patterns, and interaction history.
    """
    
    def __init__(self, data_dir="data/procedural"):
        """Initialize procedural memory."""
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Files for storing different aspects of procedural memory
        self.preferences_file = os.path.join(data_dir, "interaction_preferences.json")
        self.patterns_file = os.path.join(data_dir, "conversation_patterns.json")
        
        # Load or create preferences
        if os.path.exists(self.preferences_file):
            with open(self.preferences_file, 'r') as f:
                self.preferences = json.load(f)
        else:
            self.preferences = {
                "response_length": "medium",  # short, medium, long
                "formality": "neutral",       # casual, neutral, formal
                "detail_level": "medium",     # low, medium, high
                "communication_style": "balanced",  # empathetic, direct, technical, etc.
                "humor_level": "medium",      # none, low, medium, high
                "examples_frequency": "medium"  # none, low, medium, high
            }
            self._save_preferences()
        
        # Load or create conversation patterns
        if os.path.exists(self.patterns_file):
            with open(self.patterns_file, 'r') as f:
                self.patterns = json.load(f)
        else:
            self.patterns = {
                "common_topics": {},      # Topics the user frequently discusses
                "question_types": {},     # Types of questions the user asks
                "feedback_patterns": {},  # How the user provides feedback
                "time_patterns": {        # When the user typically interacts
                    "weekday_activity": [0] * 24,  # Hour-by-hour activity (weekdays)
                    "weekend_activity": [0] * 24   # Hour-by-hour activity (weekends)
                }
            }
            self._save_patterns()
    
    def _save_preferences(self):
        """Save interaction preferences to disk."""
        with open(self.preferences_file, 'w') as f:
            json.dump(self.preferences, f, indent=2)
    
    def _save_patterns(self):
        """Save conversation patterns to disk."""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def update_preference(self, preference, value):
        """
        Update a user interaction preference.
        
        Args:
            preference: The preference to update
            value: The new value
        """
        if preference in self.preferences:
            self.preferences[preference] = value
            self._save_preferences()
    
    def record_topic(self, topic):
        """Record a conversation topic."""
        if topic in self.patterns["common_topics"]:
            self.patterns["common_topics"][topic] += 1
        else:
            self.patterns["common_topics"][topic] = 1
        self._save_patterns()
    
    def record_question_type(self, question_type):
        """Record a type of question asked by the user."""
        if question_type in self.patterns["question_types"]:
            self.patterns["question_types"][question_type] += 1
        else:
            self.patterns["question_types"][question_type] = 1
        self._save_patterns()
    
    def record_feedback(self, feedback_type, message=None):
        """Record feedback from the user (positive, negative, neutral)."""
        if feedback_type in self.patterns["feedback_patterns"]:
            self.patterns["feedback_patterns"][feedback_type] += 1
        else:
            self.patterns["feedback_patterns"][feedback_type] = 1
        self._save_patterns()
    
    def record_interaction_time(self):
        """Record when the user is interacting with the AI."""
        now = datetime.datetime.now()
        hour = now.hour
        
        # Update appropriate time pattern
        if now.weekday() < 5:  # Weekday (0-4 are Monday-Friday)
            self.patterns["time_patterns"]["weekday_activity"][hour] += 1
        else:  # Weekend
            self.patterns["time_patterns"]["weekend_activity"][hour] += 1
        
        self._save_patterns()
    
    def get_response_guidelines(self):
        """
        Get guidelines for how to respond to the user.
        
        Returns:
            String with response guidelines based on learned preferences
        """
        guidelines = []
        
        # Response length
        if self.preferences["response_length"] == "short":
            guidelines.append("Keep responses concise and to the point.")
        elif self.preferences["response_length"] == "long":
            guidelines.append("Provide detailed, comprehensive responses.")
        
        # Formality
        if self.preferences["formality"] == "casual":
            guidelines.append("Use a casual, conversational tone.")
        elif self.preferences["formality"] == "formal":
            guidelines.append("Maintain a formal, professional tone.")
        
        # Detail level
        if self.preferences["detail_level"] == "high":
            guidelines.append("Include specific details and examples.")
        elif self.preferences["detail_level"] == "low":
            guidelines.append("Focus on the big picture without too many details.")
        
        # Communication style
        if self.preferences["communication_style"] == "empathetic":
            guidelines.append("Show empathy and focus on emotional aspects.")
        elif self.preferences["communication_style"] == "technical":
            guidelines.append("Use precise technical language and terminology.")
        elif self.preferences["communication_style"] == "direct":
            guidelines.append("Be straightforward and direct.")
        
        # Humor
        if self.preferences["humor_level"] == "high":
            guidelines.append("Incorporate appropriate humor when possible.")
        elif self.preferences["humor_level"] == "none":
            guidelines.append("Maintain a serious tone without humor.")
        
        # Examples
        if self.preferences["examples_frequency"] == "high":
            guidelines.append("Provide multiple examples to illustrate points.")
        elif self.preferences["examples_frequency"] == "none":
            guidelines.append("Focus on explanations without examples.")
        
        return "\n".join(guidelines)
    
    def get_common_interests(self, limit=3):
        """Get the user's most common conversation topics."""
        sorted_topics = sorted(
            self.patterns["common_topics"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [topic for topic, count in sorted_topics[:limit]]