import os
import argparse
import gradio as gr
from conversationbot import ConversationBot
from conversationagent import ConversationAgent

os.environ["OPENAI_API_KEY"] = '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'

def change_task():
    return gr.update(visible=True)

def change_title(title):
    return gr.update(label=("UST Agent for {}".format(title)))

if __name__ == '__main__':
    if not os.path.exists("checkpoints"):
        os.mkdir("checkpoints")
    parser = argparse.ArgumentParser()
    #edit here about tools
    parser.add_argument('--load', type=str, default="LoadGivenCourses_")
    args = parser.parse_args()
    subtask_models_cfg = {e.split('_')[0].strip(): e.split('_')[1].strip() for e in args.load.split(',')}
    
    bot = ConversationAgent()
    with gr.Blocks(css="#chatbot .overflow-y-auto{height:500px}") as demo:
        task_name = gr.Radio(choices = ['courses','events'], value=None, label='what information you want to ask')
        chatbot = gr.Chatbot(elem_id="chatbot", label="UST Agent")
        state = gr.State([])
        #need a back button
        with gr.Row(visible=False) as input_raws:
            with gr.Column(scale=0.7):
                txt = gr.Textbox(show_label=False, placeholder="Enter text and press enter").style(
                    container=False)
            with gr.Column(scale=0.3, min_width=0):
                clear = gr.Button("Clear")
            with gr.Column(scale=0.3, min_width=0):
                back = gr.Button("back")
        ##todo##
        task_name.change(bot.init_agent,[task_name],[input_raws,task_name, txt, clear])
        task_name.change(change_title,[task_name],chatbot)
        txt.submit(bot.run_text, [txt, state], [chatbot, state])
        txt.submit(lambda: "", None, txt)
        clear.click(bot.clear())
        clear.click(lambda: [], None, chatbot)
        clear.click(lambda: [], None, state)
        back.click(change_task,None,task_name)
    demo.launch(server_name="0.0.0.0", server_port=7860)
