import os
import json
import chromadb
from sentence_transformers import SentenceTransformer

class SemanticMemory:
    """
    Semantic memory stores facts and knowledge about the user.
    This includes preferences, interests, beliefs, and other
    information that defines who the user is.
    """
    
    def __init__(self, data_dir="data/semantic", model_name="all-MiniLM-L6-v2"):
        """Initialize semantic memory system."""
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # File to store structured facts
        self.facts_file = os.path.join(data_dir, "facts.json")
        
        # Load or create facts dictionary
        if os.path.exists(self.facts_file):
            with open(self.facts_file, 'r') as f:
                self.facts = json.load(f)
        else:
            self.facts = {
                "preferences": {},  # Things the user likes/dislikes
                "traits": {},       # User personality traits
                "demographics": {}, # Basic user information
                "skills": {},       # User abilities and expertise
                "values": {},       # User's core values
                "goals": [],        # User's stated goals
            }
            self._save_facts()
        
        # Initialize embedding model for similarity search
        self.embedding_model = SentenceTransformer(model_name)
        
        # Initialize ChromaDB for unstructured knowledge
        self.chroma_client = chromadb.PersistentClient(path=data_dir)
        try:
            self.collection = self.chroma_client.get_collection("semantic_knowledge")
        except:
            self.collection = self.chroma_client.create_collection("semantic_knowledge")
    
    def _save_facts(self):
        """Save facts to disk."""
        with open(self.facts_file, 'w') as f:
            json.dump(self.facts, f, indent=2)
    
    def add_preference(self, item, sentiment, confidence=1.0):
        """
        Add a user preference.
        
        Args:
            item: What the preference is about
            sentiment: Positive (like), Negative (dislike), or Neutral
            confidence: How confident we are about this preference (0.0-1.0)
        """
        self.facts["preferences"][item] = {
            "sentiment": sentiment,
            "confidence": confidence,
            "conflicts": []  # Track any conflicting preferences
        }
        
        # Check for conflicts (e.g., user liked something before but now dislikes it)
        for other_item, details in self.facts["preferences"].items():
            if other_item != item and other_item.lower() in item.lower() or item.lower() in other_item.lower():
                if details["sentiment"] != sentiment:
                    # Add conflict note
                    conflict = f"Possible conflict with '{other_item}' ({details['sentiment']})"
                    self.facts["preferences"][item]["conflicts"].append(conflict)
        
        self._save_facts()
    
    def add_trait(self, trait, value, confidence=1.0):
        """Add a user personality trait."""
        self.facts["traits"][trait] = {
            "value": value,
            "confidence": confidence
        }
        self._save_facts()
    
    def add_demographic(self, key, value):
        """Add basic user information."""
        self.facts["demographics"][key] = value
        self._save_facts()
    
    def add_skill(self, skill, level="beginner", confidence=1.0):
        """Add a user skill with proficiency level."""
        self.facts["skills"][skill] = {
            "level": level,
            "confidence": confidence
        }
        self._save_facts()
    
    def add_value(self, value, importance=1.0):
        """Add something the user values."""
        self.facts["values"][value] = {
            "importance": importance
        }
        self._save_facts()
    
    def add_goal(self, goal, timeframe=None):
        """Add a user goal."""
        self.facts["goals"].append({
            "description": goal,
            "timeframe": timeframe,
            "created": datetime.datetime.now().isoformat()
        })
        self._save_facts()
    
    def add_knowledge(self, fact, category=None):
        """
        Add an unstructured piece of knowledge about the user.
        These are facts that don't fit neatly into the structured categories.
        """
        # Create metadata
        metadata = {
            "category": category if category else "general",
            "added": datetime.datetime.now().isoformat()
        }
        
        # Create embedding
        embedding = self.embedding_model.encode(fact).tolist()
        
        # Add to collection
        self.collection.add(
            embeddings=[embedding],
            documents=[fact],
            metadatas=[metadata],
            ids=[f"knowledge_{self.collection.count()+1}"]
        )
    
    def get_relevant_knowledge(self, query, limit=5):
        """
        Retrieve knowledge relevant to the query.
        
        Args:
            query: The query to find relevant knowledge for
            limit: Maximum number of items to retrieve
            
        Returns:
            List of relevant knowledge items
        """
        # Create query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Query the collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit
        )
        
        return results["documents"][0]
    
    def get_user_profile_summary(self):
        """
        Get a concise summary of key user information.
        This is useful for including in AI prompts.
        """
        summary = []
        
        # Add demographic information
        if self.facts["demographics"]:
            demo_str = ", ".join([f"{k}: {v}" for k, v in self.facts["demographics"].items()])
            summary.append(f"Demographics: {demo_str}")
        
        # Add top preferences (likes)
        likes = [item for item, details in self.facts["preferences"].items()
                if details["sentiment"] == "positive"][:5]
        if likes:
            summary.append(f"Likes: {', '.join(likes)}")
        
        # Add top preferences (dislikes)
        dislikes = [item for item, details in self.facts["preferences"].items()
                   if details["sentiment"] == "negative"][:5]
        if dislikes:
            summary.append(f"Dislikes: {', '.join(dislikes)}")
        
        # Add key traits
        if self.facts["traits"]:
            traits_str = ", ".join([f"{k}: {v['value']}" for k, v in self.facts["traits"].items()][:5])
            summary.append(f"Traits: {traits_str}")
        
        # Add skills
        if self.facts["skills"]:
            skills_str = ", ".join([f"{k} ({v['level']})" for k, v in self.facts["skills"].items()][:5])
            summary.append(f"Skills: {skills_str}")
        
        # Add values
        if self.facts["values"]:
            values = list(self.facts["values"].keys())[:5]
            summary.append(f"Values: {', '.join(values)}")
        
        # Add goals
        if self.facts["goals"]:
            goals = [g["description"] for g in self.facts["goals"][:3]]
            summary.append(f"Goals: {', '.join(goals)}")
        
        return "\n".join(summary)