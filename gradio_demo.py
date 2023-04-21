import os
import argparse
import gradio as gr
from conversationbot import ConversationBot

os.environ["OPENAI_API_KEY"] = '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'

if __name__ == '__main__':
    if not os.path.exists("checkpoints"):
        os.mkdir("checkpoints")
    parser = argparse.ArgumentParser()
    #edit here about tools
    parser.add_argument('--load', type=str, default="ImageCaptioning_cuda:0,Text2Image_cuda:0")
    args = parser.parse_args()
    subtask_models_cfg = {e.split('_')[0].strip(): e.split('_')[1].strip() for e in args.load.split(',')}
    #
    bot = ConversationBot(subtask_models_cfg=subtask_models_cfg)
    with gr.Blocks(css="#chatbot .overflow-y-auto{height:500px}") as demo:
        lang = gr.Radio(choices = ['Chinese','English'], value=None, label='Language')
        chatbot = gr.Chatbot(elem_id="chatbot", label="UST Agent")
        state = gr.State([])
        with gr.Row(visible=False) as input_raws:
            with gr.Column(scale=0.7):
                txt = gr.Textbox(show_label=False, placeholder="Enter text and press enter").style(
                    container=False)
            with gr.Column(scale=0.3, min_width=0):
                clear = gr.Button("Clear")
    
        lang.change(bot.init_agent, [lang], [input_raws, lang, txt, clear])
        txt.submit(bot.run_text, [txt, state], [chatbot, state])
        txt.submit(lambda: "", None, txt)
        clear.click(bot.memory.clear)
        clear.click(lambda: [], None, chatbot)
        clear.click(lambda: [], None, state)
    demo.launch(server_name="0.0.0.0", server_port=7860)
