class PromptBuilder:
    """Constructs AI prompts that incorporate memory systems."""
    
    def __init__(self, working_memory, semantic_memory, episodic_memory, procedural_memory):
        """Initialize with references to all memory systems."""
        self.working_memory = working_memory
        self.semantic_memory = semantic_memory
        self.episodic_memory = episodic_memory
        self.procedural_memory = procedural_memory
    
    def build_prompt(self, current_message, context_turns=3, relevance_limit=3):
        """
        Build a comprehensive prompt incorporating all memory systems.
        
        Args:
            current_message: The user's current message
            context_turns: Number of conversation turns to include from working memory
            relevance_limit: Number of relevant memories to include
            
        Returns:
            A formatted prompt string
        """
        # Start with system instructions based on procedural memory
        prompt_parts = [
            "You are a personal AI assistant that learns from interactions.",
            "When speaking to a user for the first time or when you have limited information about them:",
            "- Respond naturally and conversationally, like a friendly assistant meeting someone new",
            "- Don't make assumptions about their interests or background",
            "- Keep initial responses brief and let the conversation develop organically",
            "- Only mention information you've actually learned from previous interactions",
            "You CANNOT set reminders or alarms as you don't have the capability to track time or send notifications.",
            "If asked about reminders or timers, politely explain this limitation."
            ]

        # Add user profile information ONLY if it actually exists
        user_profile = self.semantic_memory.get_user_profile_summary()
        if user_profile and any(line.strip() for line in user_profile.split('\n')):
            prompt_parts.append("\nWhat I know about you:")
            prompt_parts.append(user_profile)
        
        # Add relevant episodic memories
        relevant_episodes = self.episodic_memory.retrieve_relevant_episodes(current_message, limit=relevance_limit)
        if relevant_episodes:
            prompt_parts.append("\nRelevant past interactions:")
            for episode in relevant_episodes:
                # Format timestamp to be more readable
                timestamp = episode["metadata"].get("timestamp", "").split("T")[0]  # Just get the date part
                prompt_parts.append(f"- On {timestamp}: {episode['content']}")
        
        # Add common interests from procedural memory
        common_interests = self.procedural_memory.get_common_interests()
        if common_interests:
            prompt_parts.append("\nTopics you often discuss:")
            prompt_parts.append(", ".join(common_interests))
        
        # Add semantic knowledge relevant to the current message
        relevant_knowledge = self.semantic_memory.get_relevant_knowledge(current_message, limit=relevance_limit)
        if relevant_knowledge:
            prompt_parts.append("\nRelevant information about you:")
            for item in relevant_knowledge:
                prompt_parts.append(f"- {item}")
        
        # Add recent conversation context from working memory
        recent_context = self.working_memory.get_recent_context(num_turns=context_turns)
        if recent_context:
            prompt_parts.append("\nRecent conversation:")
            prompt_parts.append(recent_context)
        
        # Add the current message
        prompt_parts.append(f"\nHuman: {current_message}")
        prompt_parts.append("Assistant:")
        
        # Join all parts with appropriate spacing
        return "\n\n".join(prompt_parts)