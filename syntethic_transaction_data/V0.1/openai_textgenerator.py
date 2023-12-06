from typing import Union, Optional, List, Any
import openai
import os
from datamodel import Message, LLMResponse
from utils import num_tokens_from_messages

class TextGenerator:
    def __init__(
        self, 
        model_name: str = "gpt-3.5-turbo", 
        api_key: str = None,
        config: dict = None
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
        
        # default openai configs
        openai_config = {
            "n": config.get("n", 1),
            "temperature": config.get("temperature", 0),
            "max_tokens": config.get("max_tokens", 4096),
            "top_p": config.get("top_p", 1),
            "frequency_penalty": config.get("frequency_penalty", 0),
            "presence_penalty": config.get("presence_penalty", 0),
        }
        
        # TODO: add cache capability

        llm_response = openai.ChatCompletion.create(messages=messages, model = self.model_name, **openai_config)
        response = LLMResponse(
            text = [Message(**x.message) for x in llm_response.choices],
            config = self.config,
            usage = dict(llm_response.usage)
        )

        return response
    
    def token_usage(self, text: Union[List[dict],str]) -> int:
        return num_tokens_from_messages(text)