from typing import Any, Dict
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

class TokenUsageCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.total_tokens = 0

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        if response.llm_output and "token_usage" in response.llm_output:
            token_usage = response.llm_output["token_usage"]
            self.total_tokens += token_usage.get("total_tokens", 0)
