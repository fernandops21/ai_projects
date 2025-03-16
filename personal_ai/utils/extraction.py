import re
import nltk
from nltk.tokenize import sent_tokenize

class InformationExtractor:
    """Extracts structured information from user messages."""
    
    def __init__(self):
        """Initialize the extractor with patterns for different information types."""
        # Pattern for preferences (likes/dislikes)
        self.preference_patterns = [
            (r"I (?:really |kind of |)(?:like|love|enjoy|prefer) ([\w\s]+)", "positive"),
            (r"I (?:really |kind of |)(?:hate|dislike|don't like|can't stand) ([\w\s]+)", "negative"),
            (r"([\w\s]+) is (?:my favorite|the best)", "positive"),
            (r"([\w\s]+) is (?:terrible|the worst)", "negative")
        ]
        
        # Pattern for user traits
        self.trait_patterns = [
            r"I am (?:very |quite |extremely |somewhat |)(\w+)",
            r"I consider myself (?:very |quite |extremely |somewhat |)(\w+)",
            r"I tend to be (?:very |quite |extremely |somewhat |)(\w+)"
        ]
        
        # Pattern for skills/abilities
        self.skill_patterns = [
            r"I (?:know how to|can) ([\w\s]+)",
            r"I'm (?:good|great|excellent|skilled) at ([\w\s]+)",
            r"I have experience (?:with|in) ([\w\s]+)"
        ]
        
        # Pattern for demographic information
        self.demographic_patterns = [
            (r"I am (\d+) years old", "age"),
            (r"I work as an? ([\w\s]+)", "occupation"),
            (r"I live in ([\w\s,]+)", "location")
        ]
        
        # Pattern for goals
        self.goal_patterns = [
            r"I want to ([\w\s]+)",
            r"I'm trying to ([\w\s]+)",
            r"My goal is to ([\w\s]+)",
            r"I plan to ([\w\s]+)"
        ]
    
    def extract_preferences(self, text):
        """Extract user preferences from text."""
        preferences = []
        
        for pattern, sentiment in self.preference_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                item = match.group(1).strip().lower()
                if item and len(item) > 2:  # Avoid very short matches
                    preferences.append((item, sentiment))
        
        return preferences
    
    def extract_traits(self, text):
        """Extract user traits from text."""
        traits = []
        
        for pattern in self.trait_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                trait = match.group(1).strip().lower()
                if trait and len(trait) > 2:
                    traits.append(trait)
        
        return traits
    
    def extract_skills(self, text):
        """Extract user skills from text."""
        skills = []
        
        for pattern in self.skill_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                skill = match.group(1).strip().lower()
                if skill and len(skill) > 2:
                    skills.append(skill)
        
        return skills
    
    def extract_demographics(self, text):
        """Extract demographic information from text."""
        demographics = {}
        
        for pattern, key in self.demographic_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value = match.group(1).strip()
                if value:
                    demographics[key] = value
        
        return demographics
    
    def extract_goals(self, text):
        """Extract user goals from text."""
        goals = []
        
        for pattern in self.goal_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                goal = match.group(1).strip().lower()
                if goal and len(goal) > 3:
                    goals.append(goal)
        
        return goals
    
    def extract_all(self, text):
        """Extract all types of information from text."""
        return {
            "preferences": self.extract_preferences(text),
            "traits": self.extract_traits(text),
            "skills": self.extract_skills(text),
            "demographics": self.extract_demographics(text),
            "goals": self.extract_goals(text)
        }
    
    def extract_topics(self, text):
        """Extract potential conversation topics from text."""
        try:
            # Try to use NLTK sentence tokenizer
            sentences = sent_tokenize(text)
        except Exception as e:
            # Fallback to simple sentence splitting if tokenizer fails
            print(f"Falling back to simple sentence splitting: {e}")
            sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        
        # A very simple topic extraction - in a real system, you would use
        # more sophisticated NLP techniques like keyword extraction or named entity recognition
        topics = []
        for sentence in sentences:
            # Look for nouns and noun phrases (a simplification)
            # In a real system, use POS tagging and chunking
            words = re.findall(r'\b[A-Za-z][a-z]{3,}\b', sentence)
            for word in words:
                if word.lower() not in ["that", "this", "there", "these", "those", "what", "when", "where", "which", "who", "whom", "whose", "why", "how"]:
                    topics.append(word)
        
        return list(set(topics))  # Remove duplicates