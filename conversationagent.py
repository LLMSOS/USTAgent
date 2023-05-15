# coding: utf-8
import os
import gradio as gr
import random
import cv2
import re
import uuid
from PIL import Image, ImageDraw, ImageOps, ImageFont
import math
import numpy as np
import inspect

from langchain.agents.initialize import initialize_agent
from langchain.agents.tools import Tool
from langchain.chains.conversation.memory import ConversationBufferMemory, ConversationSummaryBufferMemory
from langchain.llms.openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.base_language import BaseLanguageModel
from gpt4f_llm import GPT4F_LLM
from langchain.llms import GPT4All
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from predefined_prompts import UST_AGENT_FORMAT_INSTRUCTIONS, UST_AGENT_PREFIX, UST_AGENT_SUFFIX

# import tools
from load_courseinfo.load import LoadGivenCourses

os.environ["OPENAI_API_KEY"] = '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'

class ConversationAgent:
    """ The conversation agent class initializes agent according to different task.
        Currently, we only support the tasks related to information that can be stored into a pandas dataframe.

        Recently supported tasks:
        - courses agent: ask anything related to courses

        Args:

    """

    def __init__(self,
                 task = "courses"):
        self.current_task = task
        
        self.llm = OpenAI(temperature=0, model_name="gpt-3.5-turbo")
        # self.llm = GPT4F_LLM(model_name='theb')
        # callbacks = [StreamingStdOutCallbackHandler()]
        # self.llm = GPT4All(model="D:\gpt4all\models\ggml-gpt4all-j-v1.3-groovy.bin", backend='gptj', verbose=True, n_threads=8)
        self.memory = ConversationSummaryBufferMemory(llm=OpenAI(temperature=0), memory_key="chat_history", output_key='output')
        self.agent = None

    def clear(self):
        self.memory.clear()

    def init_agent(self, task):
        self.memory.clear()
        place = "Enter text and press enter"
        label_clear = "Clear"
        if self.agent is not None:
            print(f"Agent will be re-initialized to task {task}.")
        # TODO: initialize agent according to task

        return gr.update(visible = True), gr.update(visible = False), gr.update(placeholder=place), gr.update(value=label_clear)
    
    def run_text(self, text, state):
        res = self.agent.run({"input": text.strip()})
        response = res['output']
        state = state + [(text, response)]
        print(f"\nProcessed run_text, Input text: {text}\nCurrent state: {state}\n"
              f"Current Memory: {self.agent.memory.buffer}")
        
        return state, state
    