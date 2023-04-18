import os
import openai
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
    print(chat_gpt('gpt-3.5-turbo','Hello'))