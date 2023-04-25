import os
import openai

from load_courseinfo.load import LoadGivenCourses
#get your key from https://platform.openai.com/account/api-keys
#available models can be found in https://platform.openai.com/docs/models
#or you can do openai.Models.list()
def chat_gpt(model_,content):
    openai.api_key = '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'

    completion = openai.ChatCompletion.create(model=model_, messages=[{"role": "user", "content": content}])
    return completion.choices[0].message.content

def file_upload_gpt(filename,purpose_):
    openai.api_key = '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'
    openai.File.create(file=open(filename), purpose=purpose_)#jsonl and fine-tune

if __name__ == '__main__':
    tool = LoadGivenCourses()
    courses = tool.forward('comp2011, comp3211, math2011')
    inputs = f'help me to select the courses\' sections into a table without time conflicts from the following: {courses}'
    with open('test.txt', 'w') as f:
        # TODO: change chat_gpt to Phoenix-chat-7b: https://github.com/FreedomIntelligence/LLMZoo
        f.write(chat_gpt('gpt-3.5-turbo',inputs))