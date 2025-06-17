import json
import os

from promptdown import StructuredPrompt
from utils.file import save_results
from utils.llm import query_llm
from utils.obm import get_obm_document_info

from config import LLM_MODEL, PROMPTS_DIR

def detect_references(minute_id, system):
    """
    Detects references to dossiers and documents in a parliamentary minute.
    """

    # Retrieve the minute text
    minute = get_obm_document_info(minute_id)
    minute_text = minute['md_content']

    if not minute_text:
        print(f"[ERROR] Could not retrieve text for minute {minute_id}")
        return None

    # Read the detection prompt template
    detection_prompt = get_detection_prompt(system)
    detection_prompt.apply_template_values({ "minute_text": minute_text })
    detection_messages = detection_prompt.to_chat_completion_messages()

    # Query the LLM for detection
    detection_response = query_llm(messages=detection_messages, model=LLM_MODEL)

    try:
        # Parse and save the detection results
        detection_data = json.loads(detection_response)
        candidate_references = detection_data.get("candidate_references", [])
        save_results(detection_data, minute_id, f"{system}-detection")
    except json.JSONDecodeError as e:
        print(f"[ERROR][detect_references] parsing detection results: {e}")
        save_results(detection_response, minute_id, f"{system}-detection-error", format="txt")
        return None

    # If using the 1-step system, return the references
    if is_single_step_system(system):
        return candidate_references

    validation_prompt = get_validation_prompt(system)
    validation_prompt.apply_template_values({ "minute_text": minute_text, "candidate_references": candidate_references })
    validation_messages = validation_prompt.to_chat_completion_messages()
    validation_response = query_llm(messages=validation_messages, model=LLM_MODEL)
    try:
        # Parse and save the validation results
        validation_data = json.loads(validation_response)
        validated_references = validation_data.get("validated_references", [])
        save_results(validation_data, minute_id, f"{system}-validation")
    except json.JSONDecodeError as e:
        print(f"[ERROR] Parsing validation results: {e}")
        save_results(validation_response, minute_id, f"{system}-validation-error", format="txt")
        return None

    return validated_references

def get_promptdown_file(prompt_name):
    """Returns the path to a promptdown file based on the prompt name."""
    file_path = os.path.join(PROMPTS_DIR, f"{prompt_name}.prompt.md")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompt file '{file_path}' does not exist.")
    return file_path

def get_detection_prompt(system):
    """Returns the appropriate prompt based on the detection system."""
    prompt = get_promptdown_file(f"{system}-detection")
    return StructuredPrompt.from_promptdown_file(prompt)

def get_validation_prompt(system):
    """Returns the appropriate prompt based on the detection system."""
    prompt = get_promptdown_file(f"{system}-validation")
    return StructuredPrompt.from_promptdown_file(prompt)

def is_single_step_system(system):
    """Checks if the detection system is a single-step system."""
    return 'single' in system