from typing import Union, Optional, List, Any
import openai
import os
from datamodel import Message, LLMResponse
from utils import num_tokens_from_messages
import requests

class TextGenerator:
    def __init__(
        self, 
        model_name: str = "gpt-3.5-turbo", 
        api_key: str = None
    ):
        api_key = os.environ.get("OPENAI_API_KEY") or None
        if api_key is None:
            raise ValueError(
                "OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable."
            )
        openai.api_key = api_key
        self.model_name = model_name or None 


    def generate(
            self, 
            messages: Union[List[dict],str],
            config: Optional[dict],
    ) ->  LLMResponse:
        
        prompt_tokens = num_tokens_from_messages(messages)
        max_tokens = max(4096 - prompt_tokens - 10, 200)

        # default openai configs
        openai_config = {
            "n": config.get("n", 1),
            "temperature": config.get("temperature", 0),
            "max_tokens": config.get("max_tokens", max_tokens),
            "top_p": config.get("top_p", 1),
            "frequency_penalty": config.get("frequency_penalty", 0),
            "presence_penalty": config.get("presence_penalty", 0),
        }
        
        # TODO: add cache capability

        try:
            llm_response = openai.ChatCompletion.create(messages=messages, model = self.model_name, **openai_config)

        except openai.error.AuthenticationError:
            print("Authentication failed. Check your API key.")
            
        except openai.error.RateLimitError:
            print("Rate limit exceeded. Try again later.")

        except openai.error.APIConnectionError:
            print("Network error. Check your internet connection.")

        except openai.error.APIError as e:
            if 'maximum token' in str(e):
                print("Maximum token limit exceeded.")
            else:
                print(f"API error: {e}")

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

        except ValueError:
            print("Invalid value provided.")

        except TypeError:
            print("Type error occurred.")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        response = LLMResponse(
            text = [Message(**x.message) for x in llm_response.choices],
            config = openai_config,
            usage = dict(llm_response.usage)
        )

        return response
    
    def token_usage(self, text: Union[List[dict],str]) -> int:
        return num_tokens_from_messages(text)