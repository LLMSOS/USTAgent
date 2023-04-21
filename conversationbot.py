# coding: utf-8
import os
import gradio as gr
import random
import torch
import cv2
import re
import uuid
from PIL import Image, ImageDraw, ImageOps, ImageFont
import math
import numpy as np
import inspect

from langchain.agents.initialize import initialize_agent
from langchain.agents.tools import Tool
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.llms.openai import OpenAI

from predefined_prompts import UST_AGENT_FORMAT_INSTRUCTIONS, UST_AGENT_PREFIX, UST_AGENT_SUFFIX

def cut_dialogue_history(history_memory, keep_last_n_words=500):
    if history_memory is None or len(history_memory) == 0:
        return history_memory
    tokens = history_memory.split()
    n_tokens = len(tokens)
    print(f"history_memory:{history_memory}, n_tokens: {n_tokens}")
    if n_tokens < keep_last_n_words:
        return history_memory
    paragraphs = history_memory.split('\n')
    last_n_tokens = n_tokens
    while last_n_tokens >= keep_last_n_words:
        last_n_tokens -= len(paragraphs[0].split(' '))
        paragraphs = paragraphs[1:]
    return '\n' + '\n'.join(paragraphs)


class ConversationBot:
    """ The conversation bot class by combining the language model and the subtask agents.    
    """

    def __init__(self,
                 subtask_models_cfg):
        self.subtask_models_cfg = subtask_models_cfg
        self.subtask_models = {}
        # instantiate the required subtask models as a global variable
        for subtask_model_name, subtask_model_cfg in subtask_models_cfg.items():
            self.subtask_models[subtask_model_name] = globals()[subtask_model_name](**subtask_model_cfg)

        print(f"All the Available Functions: {self.subtask_models}")

        self.tools = []
        # require all model classes have the method starting with "forward" to be used as a tool
        # require all tools are warped into a class with the decorator "prompts"
        for model in self.subtask_models.values():
            if hasattr(model, "forward"):
                tool = model.forward
                self.tools.append(Tool(name=tool.name, description=tool.description, func=tool))

        self.llm = OpenAI(temperature=0)
        self.memory = ConversationBufferMemory(memory_key="chat_history", output_key='output')

    def init_agent(self, lang):
        self.memory.clear()
        if lang == "English":
            PREFIX = UST_AGENT_PREFIX
            FORMAT_INSTRUCTIONS = UST_AGENT_FORMAT_INSTRUCTIONS
            SUFFIX = UST_AGENT_SUFFIX
            place = "Enter text and press enter"
            label_clear = "Clear"
        else:
            raise NotImplementedError(f"Language {lang} is not supported yet.")
        
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent="conversational-react-description",
            memory=self.memory,
            return_intermediate_steps=True,
            agent_kwargs={'prefix': PREFIX, 'format_instructions': FORMAT_INSTRUCTIONS,
                          'suffix': SUFFIX}, )
        return gr.update(visible = True), gr.update(visible = False), gr.update(placeholder=place), gr.update(value=label_clear)