import openai
from chatgpt.tools.utils import completion_with_backoff, num_tokens_from_messages, truncate_text
import json
from pathlib import Path
import sys
import os
ENV={}
with open('env.json') as env:
    ENV = json.load(env)

class Client(object):
    def __init__(self, api_key=ENV['GPTKEY'], model="gpt-3.5-turbo-0301", system_prompt=None):
        openai.api_key = api_key
        self.model = model
        self.temperature = 0.7
        self.max_tokens = 4096
        self.top_p = 1
        self.stream = False
        self.frequency_penalty = 0
        self.presence_penalty = 0
        self.system_prompt = system_prompt
        self.messages = [] if system_prompt is None else [{"role": "system", "content": system_prompt}]
    
    def create_image(self, prompt, n=1, size="1024x1024"):
        response = openai.Image.create(
            prompt=prompt,
            n=n,
            size=size
        )
        return response['data']
    
    def transcribe(self, audio):
        transcript = openai.Audio.transcribe("whisper-1", audio)
        return transcript

    def send_message(self, message):
        if type(message) == str:
            self.messages.append({"role": "user", "content": message})
        elif type(message) == dict:
            self.messages.append(message)
        elif type(message) == list:
            self.messages.extend(message)
        else:
            raise TypeError("message must be a string, dict, or list of dicts")
        
        num_tokens = num_tokens_from_messages(self.messages, self.model)
        if num_tokens > self.max_tokens:
            while len(self.messages) > 1:
                self.messages.pop(0)
                num_tokens = num_tokens_from_messages(self.messages, self.model)
                if num_tokens <= self.max_tokens:
                    break
            if num_tokens > self.max_tokens:
                self.messages[0]["content"] = truncate_text(self.messages[0]["content"], self.max_tokens, self.model)

        results = completion_with_backoff(
            model=self.model,
            messages=self.messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
        )
        self.messages.append({"role": "assistant", "content": results['choices'][0]["message"]["content"]})
        return results['choices'][0]["message"]["content"]
    
    def clear(self):
        self.messages = [] if self.system_prompt is None else [{"role": "system", "content": self.system_prompt}]
    

if __name__ == "__main__":
    client = Client()
    while True:
        message = input("You: ")
        if message == "quit":
            break
        response = client.send_message(message)
        print("Assistant: {}".format(response))
