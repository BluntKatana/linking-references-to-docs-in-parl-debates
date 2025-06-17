
import datetime
import os
import openai
import litellm

from config import GEMINI_API_KEY

os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

def query_llm(messages, model, temperature=0.2, response_format="json_object", debug=True):
    """
    Sends a prompt and user content to the OpenAI API and returns the response.

    @source https://docs.litellm.ai/docs/providers/gemini
    """
    if len(messages) == 0:
        raise ValueError("The messages list cannot be empty.")

    try:
        # Check support for response format
        if not litellm.supports_response_schema(model=model):
            raise ValueError(f"Model {model} does not support the specified response format: {response_format}")

        # Query the LLM
        response = litellm.completion(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format={
                'type': response_format,

            },
        )

        # Read the response
        message = response.choices[0].message.content
        return message

    except openai.APIError as e:
        if debug:
            print(f"OpenAI API Error: {e}")
        return None
    except Exception as e:
        if debug:
            print(f"An unexpected error occurred: {e}")
        return None