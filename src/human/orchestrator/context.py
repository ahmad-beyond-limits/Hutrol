from typing import List, Dict, Any

class ContextManager:
    """Manages context budget and transcript compaction."""
    def __init__(self, token_limit: int = 10000):
        self.token_limit = token_limit
        # For a naive approximation: 1 token ~ 4 characters.
        self.char_limit = token_limit * 4

    def compact_transcript(self, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Applies heuristic truncation to ensure we stay within budget."""
        current_chars = sum(len(msg.get("content", "")) for msg in history)
        
        if current_chars <= self.char_limit:
            return history
            
        compacted = []
        chars_used = 0
        
        # Keep system/first message always
        if history and history[0].get("role") == "system":
            compacted.append(history[0])
            chars_used += len(history[0].get("content", ""))
            history = history[1:]
            
        # Reverse iterate to keep most recent messages
        recent_messages = []
        for msg in reversed(history):
            msg_content = msg.get("content", "")
            
            # If a single message is huge (e.g. tool output), truncate it
            if len(msg_content) > 2000:
                msg_content = msg_content[:1000] + "\n...[TRUNCATED BY CONTEXT MANAGER]...\n" + msg_content[-1000:]
                
            if chars_used + len(msg_content) > self.char_limit:
                break
                
            recent_messages.append({"role": msg.get("role"), "content": msg_content})
            chars_used += len(msg_content)
            
        compacted.extend(reversed(recent_messages))
        return compacted
