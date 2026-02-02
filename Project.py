import streamlit as st
import os
import json
import time
from typing import List, Dict, Any, Optional

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ContentCrafter AI",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR BEAUTIFUL UI ---
st.markdown("""
<style>
    /* Main Background and Text */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Card Styling */
    .css-1r6slb0 {
        background-color: #262730;
        border: 1px solid #41424b;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 600;
    }
    h1 { color: #4da6ff; }
    
    /* Success/Info Boxes */
    .stSuccess, .stInfo {
        border-radius: 8px;
    }
    
    /* Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #4da6ff;
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 0;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #0073e6;
        box-shadow: 0 4px 12px rgba(77, 166, 255, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- BACKEND LOGIC (Adapted from Project.py) ---

class GoogleSearchTool:
    """Simulated Search Tool"""
    def search(self, query: str) -> Dict[str, Any]:
        time.sleep(1.5) # Simulate network latency for UI effect
        return {
            "search_results": [
                {"snippet": f"Top SEO trends for {query}: High quality content, Backlinks, AI usage."},
                {"snippet": "Recent studies show users prefer long-form, comprehensive guides."},
                {"snippet": "Keywords trending: 'Automation', 'Workflow Optimization', 'Scalability'."}
            ]
        }

# Initialize Client Wrapper
def get_client(api_key):
    try:
        from google import genai
        from google.genai import types
        
        if not api_key:
            raise ImportError("No API Key provided")
            
        client = genai.Client(api_key=api_key)
        
        # Real Client Wrapper
        class RealGeminiClient:
            def generate(self, system_inst, prompt):
                contents = [{'role': 'user', 'parts': [{'text prompt': prompt}]}]
                # Note: Adjusting for specific SDK version syntax if needed
                # utilizing simple generate_content for broad compatibility
                try:
                    response = client.models.generate_content(
                        model='gemini-2.0-flash', 
                        contents=prompt,
                        config=types.GenerateContentConfig(system_instruction=system_inst)
                    )
                    return response.text
                except Exception as e:
                    return f"Error calling API: {str(e)}"
        return RealGeminiClient()

    except ImportError:
        # Simulated Client Wrapper
        class SimulatedGeminiClient:
            def generate(self, system_instruction, prompt):
                time.sleep(2) # Simulate thinking
                if "RESEARCH" in system_instruction:
                    return json.dumps({
                        "keywords": ["AI Efficiency", "Content Scaling", "Automated Workflows", "Future of Work"],
                        "facts": ["AI cuts writing time by 60%.", "Consistency improves brand trust.", "Human-in-the-loop is best practice."]
                    })
                elif "OUTLINE" in system_instruction:
                    return "## Introduction\n- The Shift to AI\n\n## Section 1: Benefits\n- Speed\n- Cost\n\n## Section 2: Implementation\n- Tools\n\n## Conclusion\n- Summary"
                elif "DRAFTING" in system_instruction:
                    return (
                        f"# Generated Blog Post: {prompt.splitlines()[0].replace('Topic: ', '')}\n\n"
                        "## Introduction\nIn the rapidly evolving digital landscape, content is king. "
                        "However, producing consistent, high-quality content is a challenge.\n\n"
                        "## The Power of Automation\n**AI Efficiency** is transforming how we work. "
                        "Studies suggest that **AI cuts writing time by 60%**, allowing creators to focus on strategy.\n\n"
                        "## Conclusion\nEmbracing these tools is not just about speed, it's about staying competitive."
                    )
                return "Error"
        return SimulatedGeminiClient()

# --- AGENT FUNCTIONS (With UI Callbacks) ---

def run_research_agent(topic, client, status):
    status.write("🕵️ **Agent 1 (Research):** Scouring the web for facts and keywords...")
    search_tool = GoogleSearchTool()
    search_data = search_tool.search(topic)
    
    system_instruction = "RESEARCH: Extract 4 keywords and 3 facts as JSON."
    prompt = f"Topic: {topic}. Raw Data: {search_data}"
    
    response = client.generate(system_instruction, prompt)
    
    try:
        data = json.loads(response)
        status.write(f"✅ Found {len(data['keywords'])} keywords and {len(data['facts'])} facts.")
        return data
    except:
        # Fallback for demo if JSON fails
        return {
            "keywords": [" Innovation", "Tech Trends", "AI"],
            "facts": ["Fact 1: AI is growing.", "Fact 2: Automation saves time."]
        }

def run_outline_agent(topic, research_data, client, status):
    status.write("📝 **Agent 2 (Strategist):** Structuring the narrative flow...")
    
    system_instruction = "OUTLINE: Create a markdown outline based on keywords and facts."
    prompt = f"Topic: {topic}. Keywords: {research_data['keywords']}. Facts: {research_data['facts']}"
    
    outline = client.generate(system_instruction, prompt)
    status.write("✅ Outline structure finalized.")
    return outline

def run_drafting_agent(topic, outline, research_data, client, status):
    status.write("✍️ **Agent 3 (Writer):** Writing the final prose...")
    
    system_instruction = "DRAFTING: Write a blog post based on the outline."
    prompt = f"Topic: {topic}. Outline: {outline}. Facts: {research_data['facts']}"
    
    draft = client.generate(system_instruction, prompt)
    status.write("✅ Final Polish complete.")
    return draft

# --- FRONTEND LAYOUT ---

# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("---")
    api_key = st.text_input("Gemini API Key", type="password", help="Leave empty to use Simulated Mode")
    st.info("💡 **Tip:** If no key is provided, the app runs in 'Simulation Mode' so you can see the UI flow without costs.")
    st.markdown("---")
    st.markdown("**System Status**")
    if api_key:
        st.success("🟢 Connected to Gemini Live")
    else:
        st.warning("🟡 Running in Simulation Mode")

# Main Content
st.title("🤖 ContentCrafter AI")
st.markdown("#### Your Multi-Agent Blog Post Generator")
st.markdown("This tool orchestrates a team of AI agents (Researcher, Strategist, and Writer) to turn a simple topic into a comprehensive article.")

# Input Area
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        topic_input = st.text_input("Enter your blog topic:", placeholder="e.g. The Future of Quantum Computing in Healthcare")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True) # Spacer
        generate_btn = st.button("🚀 Generate Content")

# Logic Execution
if generate_btn and topic_input:
    client = get_client(api_key)
    
    # Session State to hold results
    if 'history' not in st.session_state:
        st.session_state.history = []

    st.markdown("---")
    
    # Progress Container
    with st.status("🚀 **Starting Content Pipeline...**", expanded=True) as status:
        
        # 1. Research
        start_time = time.time()
        research_data = run_research_agent(topic_input, client, status)
        
        # 2. Outline
        outline = run_outline_agent(topic_input, research_data, client, status)
        
        # 3. Drafting
        final_post = run_drafting_agent(topic_input, outline, research_data, client, status)
        
        status.update(label="✅ **Content Generation Complete!**", state="complete", expanded=False)
        total_time = round(time.time() - start_time, 2)

    # --- RESULTS DISPLAY ---
    
    # 1. Metrics Row
    m1, m2, m3 = st.columns(3)
    m1.metric("Keywords Found", len(research_data.get('keywords', [])))
    m2.metric("Processing Time", f"{total_time}s")
    m3.metric("Word Count (Approx)", len(final_post.split()))

    # 2. Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📄 Final Blog Post", "🗺️ Outline Blueprint", "🔍 Research Data"])
    
    with tab1:
        st.markdown("### Generated Article")
        st.markdown(final_post)
        st.download_button(
            label="📥 Download Markdown",
            data=final_post,
            file_name="generated_blog.md",
            mime="text/markdown"
        )
        
    with tab2:
        st.markdown(outline)
        
    with tab3:
        st.json(research_data)

elif generate_btn and not topic_input:
    st.error("Please enter a topic to begin.")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Built with Streamlit & Google Gemini</div>", unsafe_allow_html=True)
