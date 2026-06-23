import os
import logging
from typing import List, Dict, Any

# Optional Gemini integration
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

logger = logging.getLogger(__name__)

class InterviewAgent:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if HAS_GEMINI and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self.use_llm = True
            logger.info("InterviewAgent: Using Google Gemini LLM API")
        else:
            self.use_llm = False
            logger.info("InterviewAgent: Using rule-based dialog coach")

    def generate_next_message(self, chat_history: List[Dict[str, str]], target_role: str, parsed_profile: Dict[str, Any]) -> str:
        """
        Generates the next interview prompt based on session history.
        """
        if self.use_llm:
            try:
                return self._generate_message_with_llm(chat_history, target_role, parsed_profile)
            except Exception as e:
                logger.error(f"Error generating interview message with LLM: {e}. Using rules.")
                return self._generate_message_with_rules(chat_history, target_role)
        else:
            return self._generate_message_with_rules(chat_history, target_role)

    def generate_feedback(self, chat_history: List[Dict[str, str]], target_role: str) -> str:
        """
        Generates final performance evaluation summary.
        """
        if self.use_llm:
            try:
                return self._generate_feedback_with_llm(chat_history, target_role)
            except Exception as e:
                logger.error(f"Error generating feedback with LLM: {e}. Using rules.")
                return self._generate_feedback_with_rules(chat_history, target_role)
        else:
            return self._generate_feedback_with_rules(chat_history, target_role)

    def _generate_message_with_llm(self, chat_history: List[Dict[str, str]], target_role: str, parsed_profile: Dict[str, Any]) -> str:
        formatted_history = []
        for msg in chat_history:
            role_name = "Interviewer" if msg["sender"] == "coach" else "Candidate"
            formatted_history.append(f"{role_name}: {msg['message']}")
        
        history_str = "\n".join(formatted_history)

        prompt = f"""
        You are a supportive and professional Technical Interviewer. Conduct a realistic mock interview for the role of '{target_role}'.
        
        Candidate Profile Summary:
        {parsed_profile.get('summary', 'No summary provided')}
        Skills: {', '.join(parsed_profile.get('skills', []))}
        
        Conversation History:
        {history_str}
        
        Instructions:
        1. If the history is empty, welcome the user and ask them to introduce themselves.
        2. Ask only ONE question at a time. Be natural, professional, and conversational.
        3. Respond to their previous answer briefly before asking the next question.
        4. If you have already asked 3-4 questions, politely tell the candidate that the mock session has concluded and they can now request their final report.
        
        Output only your direct response as the Interviewer.
        """
        response = self.model.generate_content(prompt)
        return response.text.strip()

    def _generate_message_with_rules(self, chat_history: List[Dict[str, str]], target_role: str) -> str:
        # Count user inputs in the history
        user_msgs = [m for m in chat_history if m["sender"] == "candidate"]
        user_turn_count = len(user_msgs)

        if user_turn_count == 0:
            return (
                f"Welcome! Thanks for taking the time to meet with me today. "
                f"I'm excited to run through this mock interview for the **{target_role}** position. "
                f"To start off, could you give me a brief introduction of your background and walk me through your career journey?"
            )
        elif user_turn_count == 1:
            return (
                f"Thank you for sharing that. It's great to hear about your background. "
                f"For a {target_role} role, technical foundations are crucial. Could you describe a challenging technical project "
                f"you worked on? What role did you play, and what technical hurdles did you overcome?"
            )
        elif user_turn_count == 2:
            return (
                f"That sounds like a complex project! It's always interesting to see how developers navigate constraints. "
                f"Let's move onto a scenario-based question: If your deployment goes live and users suddenly report the "
                f"application is extremely slow, how would you go about diagnosing and troubleshooting the root cause?"
            )
        elif user_turn_count == 3:
            return (
                f"Excellent methodology for troubleshooting. System observability is indeed key. "
                f"That concludes our mock interview session! You did a wonderful job talking through your thought process. "
                f"Please click the **'Complete Session'** button above to compile your feedback and performance score."
            )
        else:
            return "The mock interview has concluded. Please click 'Complete Session' to receive your final feedback report."

    def _generate_feedback_with_llm(self, chat_history: List[Dict[str, str]], target_role: str) -> str:
        formatted_history = []
        for msg in chat_history:
            role_name = "Interviewer" if msg["sender"] == "coach" else "Candidate"
            formatted_history.append(f"{role_name}: {msg['message']}")
        
        history_str = "\n".join(formatted_history)

        prompt = f"""
        You are a Technical Recruiting Director. Analyze the following mock interview transcript for a '{target_role}' candidate.
        Provide a comprehensive feedback report in Markdown format.
        
        Transcript:
        {history_str}
        
        The report must have the following sections:
        1. ### Overall Score: (e.g. 82/100)
        2. ### Key Strengths
           (list 2-3 specific positive things about their responses)
        3. ### Areas for Improvement
           (list 2-3 specific suggestions on how to improve depth, terminology, or clarity)
        4. ### Actionable Study Plan
           (1-2 specific topics to brush up on based on their performance)
        """
        response = self.model.generate_content(prompt)
        return response.text.strip()

    def _generate_feedback_with_rules(self, chat_history: List[Dict[str, str]], target_role: str) -> str:
        user_msgs = [m for m in chat_history if m["sender"] == "candidate"]
        
        if not user_msgs:
            return "### Overall Score: 0/100\nNo candidate responses were recorded to evaluate."

        # Calculate heuristics based on reply word counts and keyword checks
        total_words = 0
        keywords_matched = 0
        tech_words = ["python", "react", "docker", "api", "database", "sql", "git", "test", "scale", "debug", "index", "observability", "log"]
        
        for msg in user_msgs:
            msg_text = msg["message"].lower()
            total_words += len(msg_text.split())
            for keyword in tech_words:
                if keyword in msg_text:
                    keywords_matched += 1

        avg_length = total_words / len(user_msgs)
        
        # Scoring logic
        score = 65  # Base score
        if avg_length > 40:
            score += 15  # Good explanation depth
        elif avg_length > 15:
            score += 8
        
        if keywords_matched >= 5:
            score += 15  # Good use of technical terms
        elif keywords_matched >= 2:
            score += 8
            
        score = min(score, 95) # Cap at 95

        report = f"""### Overall Score: {score}/100

### Key Strengths
* **Structured Responses**: You structure your explanations logically, walking through your journey and project experiences systematically.
* **Troubleshooting Logic**: Your description of diagnostics (observability, checking system logs) shows a strong systematic debugging mentality.
* **Role Alignment**: You make conscious connections between your background and the core competencies of a **{target_role}**.

### Areas for Improvement
* **Depth of Examples**: For technical questions, try to explain *why* specific tool choices were made, rather than just *what* was done. Mentioning trade-offs builds senior-level credibility.
* **Performance Metrics**: When explaining projects, reference specific quantifiers (e.g., "reduced latency by 20%", "scaled up to 10k users"). Numbers help validate engineering impact.

### Actionable Study Plan
1. **System Diagnostics**: Brush up on system performance metrics (CPU memory profiling, network latency tools).
2. **Architecture Trade-offs**: Study comparative trade-offs between SQL and NoSQL database designs for the backend requirements.
"""
        return report
