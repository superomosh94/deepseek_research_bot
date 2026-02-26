import re
import time
from rich.console import Console
from rich.panel import Panel
import nltk
from nltk.tokenize import sent_tokenize

# Download NLTK data if needed
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

console = Console()

class PromptEngine:
    """
    Handles prompt refinement and quality checking
    """
    
    def __init__(self):
        self.iteration_history = []
        self.refined_prompts = []
        
    def create_refinement_prompt(self, original_query, responses=None, iteration=1):
        """
        Create a prompt asking DeepSeek to improve the research query.
        Incorporates repetition detection and strategic pivoting.
        """
        if not responses:
            responses = []
            
        if iteration == 1 or not responses:
            # First iteration - ask for better prompt
            prompt = f"""I need to research: "{original_query}"

Before I start the actual research, I want YOU to help me create the BEST possible research prompt.

Please analyze this topic and provide:

1. KEY ASPECTS: What are the most important subtopics I should investigate?
2. SPECIFIC QUESTIONS: What exact questions should I ask to get comprehensive information?
3. KNOWLEDGE GAPS: What might be missing from my initial approach?

Then, create an IMPROVED RESEARCH PROMPT that I can use. The improved prompt should be:
- Comprehensive and well-structured
- Specific enough to get detailed answers
- Broad enough to cover all important aspects

Format your response like this:

ANALYSIS:
[Your analysis here]

IMPROVED PROMPT:
[The actual prompt I should use for research]"""
            
        else:
            # Subsequent iterations - refine based on findings
            # Check for repetition (basic check: same length or similar keywords)
            last_resp = responses[-1]
            prev_resps = responses[:-1]
            
            is_repetitive = False
            for prev in prev_resps:
                # Check for high overlap in keywords or very similar length/structure
                if len(last_resp) > 0 and abs(len(last_resp) - len(prev)) < 50:
                    is_repetitive = True
                    break
            
            # Prepare context summary
            context_summary = ""
            for i, r in enumerate(responses):
                context_summary += f"\nITERATION {i+1} SUMMARY: {r[:300]}...\n"

            strategy = "DEEP DIVE" if not is_repetitive else "STRATEGIC PIVOT"
            
            prompt = f"""We've been researching: "{original_query}"

HISTORY SO FAR:
{context_summary}

CURRENT STATUS: We are in iteration {iteration}. 
TARGET STRATEGY: {strategy}

{'[WARNING] I noticed the last response had significant overlap with previous ones. YOU MUST PIVOT.' if is_repetitive else ''}

Based on all findings above, I need you to:

1. GAP ANALYSIS: What specific aspects remain unexplored or need more detail?
2. DIVERSIFICATION: What new angle, perspective, or related subtopic should we investigate to avoid repeating ourselves?
3. DEEPER QUESTIONS: What complex technical or specific questions should we ask now?

Create a NEW research prompt that will dig deeper into the most important or unexplored aspects.

Make this prompt:
{'### MANDATORY: Explore a completely different subtopic or edge case to break the repetition. ###' if is_repetitive else '- Focused on filling the identified gaps'}
- Designed to get UNIQUE insights not covered yet
- Highly specific and technical

Format your response like this:

GAP ANALYSIS:
[What's missing]

IMPROVED PROMPT:
[The specific prompt for next research iteration]"""
        
        return prompt
    
    def extract_research_prompt(self, response):
        """
        Extract the actual research prompt from DeepSeek's response
        """
        # Try to find content after "IMPROVED PROMPT:" marker
        improved_match = re.search(r'IMPROVED PROMPT:\s*(.+?)(?:\n\n|$)', response, re.DOTALL)
        if improved_match:
            prompt = improved_match.group(1).strip()
            if prompt:
                return prompt
        
        # Try to find any quoted prompt
        quote_match = re.search(r'"([^"]+)"', response)
        if quote_match:
            quoted = quote_match.group(1)
            if len(quoted) > 50:  # Reasonable prompt length
                return quoted
        
        # If no clear markers, use the last paragraph
        paragraphs = response.split('\n\n')
        if paragraphs:
            last_para = paragraphs[-1].strip()
            if len(last_para) > 50 and '?' in last_para:
                return last_para
        
        # Fallback: use the whole response but truncate if too long
        if len(response) > 500:
            return response[:500] + "..."
        return response
    
    def evaluate_response_quality(self, response, original_query):
        """
        Evaluate how comprehensive the response is
        Returns: (score, should_continue, reason)
        """
        if not response or len(response) < 200:
            return 0.2, True, "Response too short"
        
        # Initialize scoring factors
        score = 0.0
        factors = []
        
        # Factor 1: Length (0-0.3)
        length_score = min(len(response) / 3000, 0.3)
        score += length_score
        factors.append(f"Length: {length_score:.2f}")
        
        # Factor 2: Structure (0-0.2)
        has_sections = bool(re.search(r'#{1,3}\s+\w+|^\d+\.\s+\w+', response, re.MULTILINE))
        has_bullets = '•' in response or '-' in response or '*' in response
        structure_score = (0.1 if has_sections else 0) + (0.1 if has_bullets else 0)
        score += structure_score
        factors.append(f"Structure: {structure_score:.2f}")
        
        # Factor 3: Comprehensiveness indicators (0-0.3)
        indicators = [
            'example', 'instance', 'such as',
            'important', 'significant', 'crucial',
            'however', 'although', 'despite',
            'first', 'second', 'finally',
            'conclusion', 'summary', 'overall',
            'research shows', 'studies indicate',
            'according to', 'based on'
        ]
        
        indicator_count = sum(1 for ind in indicators if ind in response.lower())
        indicator_score = min(indicator_count / 15, 0.3)
        score += indicator_score
        factors.append(f"Indicators: {indicator_score:.2f}")
        
        # Factor 4: Relevance to query (0-0.2)
        query_words = set(original_query.lower().split())
        response_words = set(response.lower().split())
        common_words = query_words.intersection(response_words)
        relevance_score = min(len(common_words) / max(len(query_words), 1) * 0.2, 0.2)
        score += relevance_score
        factors.append(f"Relevance: {relevance_score:.2f}")
        
        # Cap at 1.0
        final_score = min(score, 1.0)
        
        # Decision logic
        if final_score >= 0.8:
            return final_score, False, f"High quality ({final_score:.1%})"
        elif len(self.iteration_history) >= 5:
            return final_score, False, f"Max iterations reached ({final_score:.1%})"
        else:
            return final_score, True, f"Need improvement ({final_score:.1%})"
    
    def generate_follow_up_questions(self, response, original_query):
        """
        Generate follow-up questions based on the response
        """
        prompt = f"""Based on this research about "{original_query}":

{response[:1000]}...

What are the 3 most important follow-up questions I should ask to deepen my understanding?
List only the questions, one per line, starting with "Q:". Make them specific and insightful."""

        return prompt
    
    def log_iteration(self, iteration_num, prompt, response, quality_score, refined_prompt):
        """Log each iteration for history"""
        self.iteration_history.append({
            'iteration': iteration_num,
            'refinement_prompt': prompt[:100] + "...",
            'research_prompt': refined_prompt[:100] + "...",
            'response_length': len(response),
            'quality_score': quality_score,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        })
