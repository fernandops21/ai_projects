from sentence_transformers import SentenceTransformer

class EmbeddingUtility:
    """Utility for creating and working with embeddings."""
    
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """Initialize with a sentence transformer model."""
        self.model = SentenceTransformer(model_name)
    
    def create_embedding(self, text):
        """Create an embedding vector for the given text."""
        return self.model.encode(text).tolist()
    
    def calculate_similarity(self, text1, text2):
        """Calculate similarity between two texts."""
        embedding1 = self.model.encode(text1)
        embedding2 = self.model.encode(text2)
        
        # Cosine similarity
        similarity = self.model.util.pytorch_cos_sim(embedding1, embedding2).item()
        return similarity