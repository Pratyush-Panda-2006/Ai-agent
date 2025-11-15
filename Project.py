import os
import json
from typing import List, Dict, Any, Optional

API_KEY = os.environ.get(AIzaSyDlmOLksuXWWfwfrOmV3J4LjjFld7S6bQY)
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it up in Kaggle Secrets.")
        
client = genai.Client(api_key=API_KEY)

# Import the necessary client
try:
    from google import genai
    from google.genai import types
    
    # --- API KEY INTEGRATION POINT ---
    # The API key should be loaded from the Kaggle Secrets Utility
    # If running locally, you can use: os.environ.get('GEMINI_API_KEY')
    API_KEY = os.environ.get('GEMINI_API_KEY')
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it up in Kaggle Secrets.")
        
    client = genai.Client(api_key=API_KEY)
    
    # Define a default model
    MODEL_NAME = 'gemini-2.5-flash'
    
    # Override the simulated generate_content method to use the real client
    def real_generate_content(
        system_instruction: str,
        prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        
        # Prepare the request contents
        contents = [{'role': 'user', 'parts': [{'text': prompt}]}]
        
        # Prepare the system instruction
        config = types.GenerateContentConfig(
            system_instruction=system_instruction
        )
        
        # Note: Tools can be added here if you were using built-in Gemini tools.
        # For this example, we're using custom Python function tools outside of the LLM call.

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=config
        )
        return response.text

except ImportError:
    # Fallback to the simulated client if the SDK isn't installed (e.g., for testing environment)
    print("Warning: Google GenAI SDK not found. Using SimulatedGeminiClient.")
    class SimulatedGeminiClient:
        """A placeholder for the Gemini client to demonstrate the API structure."""
        def generate_content(self, contents: List[Dict[str, Any]], system_instruction: str, tools: Optional[List[Dict[str, Any]]] = None) -> str:
            prompt = contents[-1]['parts'][0]['text']
            
            # Simulate different agent responses
            if "RESEARCH" in system_instruction:
                print("  [Simulated LLM Response] Researching and generating data...")
                return json.dumps({
                    "keywords": ["AI Content Generation", "Blog Automation", "SEO Strategies", "Content Marketing Trends"],
                    "facts": ["AI agents reduce drafting time by up to 70%.", "SEO optimization is crucial for organic reach.", "Multi-agent systems improve output quality."]
                })
            elif "OUTLINE" in system_instruction:
                print("  [Simulated LLM Response] Creating outline structure...")
                return "## Introduction\n- The Pain of Manual Content Creation\n\n## Section 1: Why Automation is Necessary\n- Time vs. Quality\n\n## Section 2: The Multi-Agent Solution\n- Roles of the Research and Drafting Agents\n\n## Conclusion\n- Future of AI in Content"
            elif "DRAFTING" in system_instruction:
                print("  [Simulated LLM Response] Drafting content based on outline...")
                return (
                    "# The ContentCrafter: AI-Powered Blog Post Automation\n\n"
                    "## Introduction\nCreating high-quality content consistently is a massive hurdle for many. "
                    "The 'ContentCrafter' agent is designed to solve this by automating the research and drafting process.\n\n"
                    "## Section 1: Why Automation is Necessary\nStudies show that manual content drafting can take up to 10 hours per post. "
                    "With **AI Content Generation**, agents can reduce this time significantly, leading to better **SEO Strategies** and overall content output. "
                    "AI agents reduce drafting time by up to 70%.\n\n"
                    "## Section 2: The Multi-Agent Solution\nOur system uses a multi-agent approach to ensure quality. The Research Agent focuses on facts and keywords, while the Drafting Agent focuses on narrative flow. This separation of concerns is why **Multi-agent systems improve output quality**.\n\n"
                    "## Conclusion\nBy leveraging the power of specialized AI agents, we can dramatically scale **Content Marketing Trends** and delivery, making consistent, optimized content achievable for everyone."
                )
            else:
                return "An empty response."
    
    client = SimulatedGeminiClient()
    # Define a helper function to match the structure of the real SDK call
    def real_generate_content(system_instruction: str, prompt: str, tools: Optional[List[Dict[str, Any]]] = None) -> str:
        contents=[{'role': 'user', 'parts': [{'text': prompt}]}]
        # Pass the arguments to the simulated client
        return client.generate_content(contents=contents, system_instruction=system_instruction, tools=tools)

class GoogleSearchTool:
    """A simulated tool for the Research Agent to use. Replace this with a real search API call (e.g., using Google Search Grounding or a custom Google Search API wrapper)."""
    def search(self, query: str) -> Dict[str, Any]:
        """Simulates finding relevant SEO data and facts for the topic."""
        print(f"  [Tool Call] Executing Google Search for: '{query}'")
        # In a real environment, this would call a real search API.
        # This simulated output is designed to feed the Research Agent.
        return {
            "search_results": [
                {"snippet": "Top SEO keywords for content creation: 'AI Content Generation', 'Blog Automation', 'Content Marketing Trends'."},
                {"snippet": "A recent study found multi-agent systems significantly improve output quality compared to single-agent LLM calls."}
            ]
        }

# Initialize simulated search tool
search_tool = GoogleSearchTool()

# --- 2. AGENT DEFINITIONS ---

def research_agent(topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent 1: Gathers initial facts, keywords, and performs web search.
    Demonstrates: Tool-Use, Context Engineering
    """
    print("\n[AGENT 1: RESEARCH AGENT] Starting research...")

    # 1. Use the search tool to get raw data
    search_data = search_tool.search(f"SEO keywords and current facts about: {topic}")

    # 2. Prepare the prompt for the LLM to process the raw data
    search_results_text = json.dumps(search_data, indent=2)

    system_instruction = (
        "You are a world-class Research Analyst. Your task is to process raw search results "
        "and extract the most relevant SEO keywords (4-5 max) and 3 key facts. "
        "Format the output as a JSON object with keys 'keywords' (list of strings) and 'facts' (list of strings). "
        "The response MUST be valid JSON."
    )

    llm_prompt = f"Topic: {topic}\n\nRaw Search Results:\n{search_results_text}\n\nExtract the requested structured data."

    # 3. Call the LLM to structure the research data
    research_json = real_generate_content(
        prompt=llm_prompt,
        system_instruction=system_instruction
    )

    try:
        research_data = json.loads(research_json)
        context['research_data'] = research_data
        print(f"  [Success] Research complete. Found {len(research_data['keywords'])} keywords and {len(research_data['facts'])} facts.")
    except json.JSONDecodeError as e:
        print(f"  [Error] Research Agent failed to parse JSON: {e}. Raw response: {research_json}")
        context['research_data'] = {'keywords': [], 'facts': []}
    
    return context

def outline_agent(topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent 2: Creates a structured outline based on the research.
    Demonstrates: Context Engineering, Sequential Execution
    """
    print("\n[AGENT 2: OUTLINE AGENT] Creating blog outline...")

    research_data = context.get('research_data', {})
    
    if not research_data.get('keywords') or not research_data.get('facts'):
        print("  [Failure] Missing research data. Skipping outline.")
        context['outline'] = ""
        return context

    system_instruction = (
        "You are an expert Content Strategist. Your task is to create a comprehensive, engaging, and "
        "SEO-friendly blog post outline using the provided topic, keywords, and facts. "
        "The outline must be in Markdown format with clear H2 (##) and H3 (###) headers."
    )

    llm_prompt = (
        f"Topic: {topic}\n"
        f"Target Keywords: {', '.join(research_data['keywords'])}\n"
        f"Key Facts to Include: {'; '.join(research_data['facts'])}\n\n"
        "Generate a detailed, full blog post outline in Markdown."
    )

    # 3. Call the LLM to generate the outline
    outline = real_generate_content(
        prompt=llm_prompt,
        system_instruction=system_instruction
    )
    
    context['outline'] = outline
    print(f"  [Success] Outline created (Length: {len(outline)} characters).")
    
    return context

def drafting_agent(topic: str, context: Dict[str, Any]) -> str:
    """
    Agent 3: Writes the final blog post draft based on the outline and research.
    Demonstrates: Session Memory (via context), Final Output Generation
    """
    print("\n[AGENT 3: DRAFTING AGENT] Drafting final blog post...")
    
    outline = context.get('outline', "")
    research_data = context.get('research_data', {})

    if not outline:
        return "ERROR: Cannot draft the post. Outline is missing."

    system_instruction = (
        "You are a Professional Content Writer. Your task is to write a compelling and well-researched "
        "blog post in Markdown format. Use the provided outline, facts, and keywords to write a "
        "minimum 500-word post. Ensure natural flow and engaging prose."
    )

    llm_prompt = (
        f"Topic: {topic}\n"
        f"Outline to Follow:\n{outline}\n\n"
        f"Keywords to Integrate: {', '.join(research_data.get('keywords', []))}\n"
        f"Key Facts to Reference: {'; '.join(research_data.get('facts', []))}\n\n"
        "Write the complete blog post following this structure."
    )

    # 3. Call the LLM to generate the final draft
    final_draft = real_generate_content(
        prompt=llm_prompt,
        system_instruction=system_instruction
    )
    
    return final_draft

# --- 3. ORCHESTRATOR / MAIN EXECUTION FLOW ---

def run_content_crafter(topic: str) -> str:
    """
    Orchestrates the multi-agent system in a sequential pipeline.
    Demonstrates: Multi-Agent System (Orchestration)
    """
    print("--- CONTENT CRAFTER AGENT SYSTEM INITIATED ---")
    print(f"Goal: Generate a blog post on '{topic}'")
    
    # Context dictionary acts as the "session memory" passed between agents
    context: Dict[str, Any] = {'topic': topic}
    
    # Step 1: Research
    context = research_agent(topic, context)
    
    # Step 2: Outline
    context = outline_agent(topic, context)
    
    # Step 3: Drafting (produces final output)
    final_post = drafting_agent(topic, context)
    
    print("\n--- PROCESS COMPLETE ---")
    
    # Add a final check to ensure the output is not an error message
    if final_post.startswith("ERROR"):
        return final_post

    # Final cleanup/formatting (simulated human editor step)
    final_post = final_post.strip()
    
    return final_post

# --- EXECUTION ---
if __name__ == "__main__":
    # The topic for your automated blog post
    blog_topic = "The Impact of Multi-Agent Systems on Modern Content Marketing"
    
    # Run the orchestrated system
    generated_blog_post = run_content_crafter(blog_topic)
    
    print("\n" + "="*50)
    print("FINAL GENERATED BLOG POST:")
    print("="*50)
    print(generated_blog_post)
    print("="*50)
    
    # Display the steps taken and key concepts used
    print("\nCAPSTONE PROJECT KEY CONCEPTS DEMONSTRATED:")
    print("1. Multi-Agent System: Three specialized agents (Research, Outline, Drafting) work in a pipeline.")
    print("2. Tool Use: The Research Agent utilizes the GoogleSearchTool (simulated) for information retrieval.")
    print("3. Context Engineering / Session Memory: Context is passed between agents, allowing the Drafting Agent to access data gathered by the Research Agent.")
    print("4. Sequential Orchestration: The main function manages the step-by-step execution of agents.")