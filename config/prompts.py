import yaml
import os

def load_tools_for_prompt():
    tools_path = os.path.join("config", "tools.yaml")
    if os.path.exists(tools_path):
        with open(tools_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}

INITIAL_ANALYSIS_PROMPT = """
You are an expert OSINT analyst.
Analyze the provided image, any extracted metadata (EXIF, barcodes, OCR text), and the user's context.

Identify what type of investigation this is (e.g., person, location, object, document, network).
List what you can determine from the inputs.

Available Tools:
{tools_yaml}

Based on your findings, what tools from the provided list would you run next to further the investigation?

Respond ONLY with a valid JSON object matching this schema:
{{
  "findings": ["finding 1", "finding 2"],
  "confidence": "high|medium|low",
  "tools_to_run": [
    {{"tool_name": "Name of tool", "reason": "Why run it", "input_data": "Data to feed it"}}
  ],
  "cant_determine": ["what is missing", "what cannot be verified"]
}}
"""

FINAL_SYNTHESIS_PROMPT = """
You are an expert OSINT analyst. You have completed an investigation.
Here is the initial extracted data, the tools that were run, and their results.

Initial Context: {user_context}
Initial Extracted Data: {extracted_data}
Tool Results: {tool_results}

Synthesize these findings into a final report.
If there are unresolved questions or the investigation isn't fully solved, provide a clear, step-by-step manual investigation guide with direct links to tools the user can try themselves.

Format the response in Markdown. Do not include raw JSON.
"""
