class WorkingMemory:
    """
    Working memory stores the recent conversation context.
    This is essentially the short-term memory that holds
    the current conversation flow.
    """
    
    def __init__(self, max_turns=10):
        """Initialize working memory with maximum number of conversation turns to remember."""
        self.max_turns = max_turns
        self.messages = []
    
    def add_exchange(self, user_message, ai_response):
        """Add a conversation exchange to working memory."""
        self.messages.append({
            "role": "user",
            "content": user_message
        })
        self.messages.append({
            "role": "assistant",
            "content": ai_response
        })
        
        # Trim to max_turns if needed
        if len(self.messages) > self.max_turns * 2:
            # Remove oldest exchanges (keep max_turns)
            self.messages = self.messages[-(self.max_turns * 2):]
    
    def get_recent_context(self, num_turns=None):
        """Get recent conversation turns as formatted context."""
        if num_turns is None:
            num_turns = self.max_turns
        
        # Limit to available turns (not more than we have)
        num_turns = min(num_turns, len(self.messages) // 2)
        
        # Format the recent conversations
        formatted_context = ""
        for i in range(-num_turns * 2, 0, 2):
            if abs(i) <= len(self.messages):
                user_msg = self.messages[i]
                ai_msg = self.messages[i+1] if i+1 < 0 else {"content": ""}
                formatted_context += f"Human: {user_msg['content']}\nAssistant: {ai_msg['content']}\n\n"
        
        return formatted_context.strip()
    
    def clear(self):
        """Clear working memory."""
        self.messages = []