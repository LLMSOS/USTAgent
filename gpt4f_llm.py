from typing import List, Optional, Any, Dict, Tuple

import gpt4free
from gpt4free import Provider, forefront, quora
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.openai import BaseOpenAI, OpenAIChat, _streaming_response_template, _update_response, update_token_usage
from langchain.llms.base import BaseLLM
from langchain.schema import LLMResult, Generation
from langchain.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from pydantic import Extra, Field


class GPT4F_LLM(BaseLLM):

    model_name: str = "theb"
    token: Optional[str] = None
    prefix_messages: List = Field(default_factory=list)
    """Series of messages for Chat input."""
    streaming: bool = False
        
    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.ignore
    
    def gpt_answer(self, messages, **kwargs):
        import ipdb; ipdb.set_trace()
        if self.model_name == "theb":
            provider = Provider.Theb
        elif self.model_name == "you":
            provider = Provider.You
        elif self.model_name == "forefront":
            provider = Provider.ForeFront
        elif self.model_name == "poe":
            provider = Provider.Poe
        else:
            raise NotImplementedError(f"Model {self.model_name} is not supported yet.")
        messages = messages[0]
        messages = messages["content"]
        if self.model_name == "theb" or self.model_name == "you":
            response = gpt4free.Completion.create(provider, prompt=messages)
        elif self.model_name == "forefront":
            if self.token is None:
                self.token = forefront.Account.create(logging=False)
            response = gpt4free.Completion.create(provider, prompt=messages, model='gpt-4', account_data=self.token)
        elif self.model_name == "poe":
            if self.token is None:
                self.token = quora.Account.create(logging=False)
            response = gpt4free.Completion.create(provider, prompt=messages, model='ChatGPT', token=self.token)
        return response

    async def agpt_answer(self, messages, **kwargs):
        return self.gpt_answer(messages, **kwargs)
    
    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API."""
        # return empty dict
        return {}
        
    
    def _get_chat_params(
        self, prompts: List[str], stop: Optional[List[str]] = None
    ) -> Tuple:
        if len(prompts) > 1:
            raise ValueError(
                f"OpenAIChat currently only supports single prompt, got {prompts}"
            )
        messages = self.prefix_messages + [{"role": "user", "content": prompts[0]}]
        params: Dict[str, Any] = {**{"model": self.model_name}, **self._default_params}
        if stop is not None:
            if "stop" in params:
                raise ValueError("`stop` found in both the input and default params.")
            params["stop"] = stop
        if params.get("max_tokens") == -1:
            # for ChatGPT api, omitting max_tokens is equivalent to having no limit
            del params["max_tokens"]
        return messages, params

    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> LLMResult:
        import ipdb; ipdb.set_trace()
        messages, params = self._get_chat_params(prompts, stop)
        if self.streaming:
            response = ""
            params["stream"] = True
            for stream_resp in self.gpt_answer(messages=messages, **params):
                token = stream_resp["choices"][0]["delta"].get("content", "")
                response += token
                if run_manager:
                    run_manager.on_llm_new_token(
                        token,
                    )
            return LLMResult(
                generations=[[Generation(text=response)]],
            )
        else:
            full_response = self.gpt_answer(messages=messages, **params)
            return LLMResult(
                generations=[
                    [Generation(text=full_response)]
                ]
            )
        
    async def _agenerate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
    ) -> LLMResult:
        """Call out to OpenAI's endpoint async with k unique prompts."""
        params = self._invocation_params
        sub_prompts = self.get_sub_prompts(params, prompts, stop)
        choices = []
        token_usage: Dict[str, int] = {}
        # Get the token usage from the response.
        # Includes prompt, completion, and total tokens used.
        _keys = {"completion_tokens", "prompt_tokens", "total_tokens"}
        for _prompts in sub_prompts:
            if self.streaming:
                if len(_prompts) > 1:
                    raise ValueError("Cannot stream results with multiple prompts.")
                params["stream"] = True
                response = _streaming_response_template()
                async for stream_resp in await self.agpt_answer(
                    prompt=_prompts, **params
                ):
                    if run_manager:
                        await run_manager.on_llm_new_token(
                            stream_resp["choices"][0]["text"],
                            verbose=self.verbose,
                            logprobs=stream_resp["choices"][0]["logprobs"],
                        )
                    _update_response(response, stream_resp)
                choices.extend(response["choices"])
            else:
                response = await self.agpt_answer(prompt=_prompts, **params)
                choices.extend(response["choices"])
            if not self.streaming:
                # Can't update token usage if streaming
                update_token_usage(_keys, response, token_usage)
        return self.create_llm_result(choices, prompts, token_usage)
    
    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "gpt4-free"
