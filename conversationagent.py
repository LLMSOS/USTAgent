# coding: utf-8
import os
import gradio as gr
from datetime import datetime
import time
import pandas as pd

from langchain.chains.conversation.memory import ConversationSummaryBufferMemory
from langchain.llms.openai import OpenAI

# import tools for extract information
from get_courses import crawl_website
from get_events import get_events_by_dates
from custom_agents import create_course_agent, create_event_agent, get_course_dataframes, get_event_dataframes

os.environ["OPENAI_API_KEY"] = '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'

class ConversationAgent:
    """ The conversation agent class initializes agent according to different task.
        Currently, we only support the tasks related to information that can be stored into a pandas dataframe.

        Recently supported tasks:
        - courses agent: ask anything related to courses

        Args:

    """

    def __init__(self,
                 task: str=None):
        self.current_task = task
        
        self.llm = OpenAI(temperature=0, model_name="gpt-3.5-turbo")
        # self.llm = GPT4F_LLM(model_name='theb')
        # callbacks = [StreamingStdOutCallbackHandler()]
        # self.llm = GPT4All(model="D:\gpt4all\models\ggml-gpt4all-j-v1.3-groovy.bin", backend='gptj', verbose=True, n_threads=8)
        self.memory = ConversationSummaryBufferMemory(llm=OpenAI(temperature=0), memory_key="chat_history", output_key='output')
        self.agent = None

    def clear(self):
        self.memory.clear()

    def init_agent(self, task, force_reload=False):
        self.memory.clear()
        place = "Enter text and press enter"
        label_clear = "Clear"
        if self.agent is not None:
            print(f"Agent changed from task {self.current_task} to task {task}.")
        # TODO: initialize agent according to task
        self.current_task = task
        os.makedirs(os.path.join(os.getcwd(), "data"), exist_ok=True)
        dataframes = []
        start_time = time.time()
        if task == "courses":
            info_path = os.path.join(os.getcwd(), "data", "courses_info.csv")
            section_path = os.path.join(os.getcwd(), "data", "courses_section.csv")
            if os.path.exists(info_path) and os.path.exists(section_path) and not force_reload:
                info_dataframe = pd.read_csv(info_path)
                section_dataframe = pd.read_csv(section_path)
            else:
                info_dataframe, section_dataframe = crawl_website()
                info_dataframe.to_csv(info_path, index=False)
                section_dataframe.to_csv(section_path, index=False)
            section, info = get_course_dataframes(info_path=info_path, section_path=section_path)
            self.agent = create_course_agent(llm=OpenAI(temperature=0), 
                                             df_course_info=info, 
                                             df_course_section=section,
                                             verbose=True)
        elif task == "events":
            # get the date of today
            today = datetime.today().strftime('%Y-%m-%d')
            period = 15
            # get the events of the next 15 days
            path = os.path.join(os.getcwd(), "data", f"events_{today}_to_{period}days.csv")
            if os.path.exists(path) and not force_reload:
                events = pd.read_csv(path)
            else:
                events = get_events_by_dates(today, period)
                events.to_csv(path, index=False)
            section, info = get_event_dataframes(path=path)
            self.agent = create_event_agent(llm=OpenAI(temperature=0), 
                                            df_event_section=section,
                                            df_event_info=info,
                                            verbose=True)
        else:
            raise ValueError(f"Task {task} is not supported yet.")
        cost = time.time() - start_time
        print(f"Time cost for initiation: {cost}")
        return gr.update(visible = True), gr.update(visible = False), gr.update(placeholder=place), gr.update(value=label_clear)
    
    def run_text(self, text, state):
        res = self.agent.run({"input": text.strip()})
        response = res
        state = state + [(text, response)]
        print(f"\nProcessed run_text, Input text: {text}\nCurrent state: {state}\n")
            #   f"Current Memory: {self.agent.memory.buffer}")
        self.memory.save_context(inputs=text, outputs=response)
        return state, state
    

if __name__ == "__main__":
    agent = ConversationAgent()
    agent.init_agent("courses")