import os
import json
import datetime
import chromadb
import uuid
from sentence_transformers import SentenceTransformer

class EpisodicMemory:
    """
    Episodic memory stores specific interactions and events.
    These are concrete experiences with timestamps that capture
    specific moments in your history with the AI.
    """
    
    def __init__(self, data_dir="data/episodic", model_name="all-MiniLM-L6-v2"):
        """Initialize episodic memory with embedding model."""
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(model_name)
        
        # Initialize ChromaDB client and collection
        self.chroma_client = chromadb.PersistentClient(path=data_dir)
        try:
            self.collection = self.chroma_client.get_collection("episodes")
        except:
            self.collection = self.chroma_client.create_collection("episodes")
    
    def add_episode(self, content, importance=1.0, metadata=None):
        """
        Add a new episode to memory.
        
        Args:
            content: The content of the episode (e.g., a message or event)
            importance: A rating of importance (1.0-5.0)
            metadata: Additional information about the episode
        """
        if metadata is None:
            metadata = {}
        
        # Create a unique ID for this episode
        episode_id = str(uuid.uuid4())
        
        # Add timestamp
        timestamp = datetime.datetime.now().isoformat()
        
        # Combine metadata
        full_metadata = {
            "timestamp": timestamp,
            "importance": float(importance),
            **metadata
        }
        
        # Create embedding
        embedding = self.embedding_model.encode(content).tolist()
        
        # Add to collection
        self.collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[full_metadata],
            ids=[episode_id]
        )
        
        return episode_id
    
    def retrieve_relevant_episodes(self, query, limit=5):
        """
        Retrieve episodes relevant to the given query.
        
        Args:
            query: The query to find relevant episodes for
            limit: Maximum number of episodes to retrieve
            
        Returns:
            List of relevant episodes with their content and metadata
        """
        # Create query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Query the collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            include=["documents", "metadatas"]
        )
        
        # Format results
        episodes = []
        for i in range(len(results["documents"][0])):
            episodes.append({
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i]
            })
        
        return episodes
    
    def retrieve_recent_episodes(self, limit=5):
        """Retrieve the most recent episodes."""
        # This is a simplified implementation - in a real system,
        # you would query by recency using the metadata
        all_ids = self.collection.get(include=["metadatas"])["metadatas"]
        
        # Sort by timestamp (most recent first)
        sorted_ids = sorted(
            range(len(all_ids)),
            key=lambda i: all_ids[i].get("timestamp", ""),
            reverse=True
        )
        
        # Get the most recent IDs
        recent_ids = [all_ids[i].get("id", "") for i in sorted_ids[:limit]]
        
        # Retrieve those episodes
        results = self.collection.get(
            ids=recent_ids,
            include=["documents", "metadatas"]
        )
        
        # Format results
        episodes = []
        for i in range(len(results["documents"])):
            episodes.append({
                "content": results["documents"][i],
                "metadata": results["metadatas"][i]
            })
        
        return episodes