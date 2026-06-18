from typing import List, Dict

class MemorySummarizer:
    def summarize_recent_turns(self, turns: List[Dict[str, str]]) -> str:
        """
        Convert recent turns into a concise string format.
        """
        if not turns:
            return "No previous turns in this session."
        
        # Take the last 5 turns to keep it concise
        recent = turns[-5:]
        summary_lines = []
        for turn in recent:
            role = "Student" if turn["role"] == "user" else "Assistant"
            content = turn["content"]
            # Truncate very long turns in the summary
            if len(content) > 200:
                content = content[:197] + "..."
            summary_lines.append(f"{role}: {content}")
            
        return "\n".join(summary_lines)

memory_summarizer = MemorySummarizer()
