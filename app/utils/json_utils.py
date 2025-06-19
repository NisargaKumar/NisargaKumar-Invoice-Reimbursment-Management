import json
import re

def extract_json_from_llm_response(response_text: str):
    try:
        return json.loads(response_text.strip())
    except json.JSONDecodeError:
        cleaned = re.sub(r"^```(json)?|```$", "", response_text.strip(), flags=re.MULTILINE)
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return {"error": "Malformed JSON after cleanup"}
        else:
            return {"error": "No valid JSON found"}
