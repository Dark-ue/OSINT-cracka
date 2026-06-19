import os
import json
import google.generativeai as genai
from config.prompts import INITIAL_ANALYSIS_PROMPT, FINAL_SYNTHESIS_PROMPT
from app.utils import get_tools_config

def setup_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_key_here":
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash')

def get_initial_strategy(image_path, extracted_data, user_context):
    """Gets initial analysis and tool recommendations from Gemini."""
    model = setup_gemini()
    if not model:
        return {"error": "Gemini API key not configured properly."}

    tools_yaml = json.dumps(get_tools_config(), indent=2)
    prompt = INITIAL_ANALYSIS_PROMPT.format(tools_yaml=tools_yaml)
    
    contents = [prompt, f"User Context: {user_context}\nExtracted Data: {json.dumps(extracted_data)}"]
    
    if image_path and os.path.exists(image_path):
        try:
             # Upload file to Gemini for vision capabilities
             sample_file = genai.upload_file(path=image_path)
             contents.append(sample_file)
        except Exception as e:
             contents.append(f"Image upload failed: {e}")

    try:
        response = model.generate_content(
            contents,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": f"Failed to get strategy from Gemini: {e}"}

def synthesize_findings(user_context, extracted_data, tool_results):
    """Gets final markdown report from Gemini."""
    model = setup_gemini()
    if not model:
        return "Gemini API key not configured properly. Cannot synthesize."

    prompt = FINAL_SYNTHESIS_PROMPT.format(
        user_context=user_context,
        extracted_data=json.dumps(extracted_data),
        tool_results=json.dumps(tool_results)
    )

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Failed to synthesize findings: {e}"


