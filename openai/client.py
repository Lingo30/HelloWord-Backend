import openai
from openai.tools.utils import completion_with_backoff, num_tokens_from_messages
class Clinet(object):
    def __init__(self, api_key="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", model="gpt-3.5-turbo-0301"):
        openai.api_key = api_key
        self.model = model
        self.temperature = 0
        self.max_tokens = 2048
        self.top_p = 1
        self.stream = False
        self.frequency_penalty = 0
        self.presence_penalty = 0
        self.messages = []

    def send_message(self, message):
        if type(message) == str:
            self.messages.append({"role": "user", "content": message})
        elif type(message) == dict:
            self.messages.append(message)
        elif type(message) == list:
            self.messages.extend(message)
        else:
            raise TypeError("message must be a string, dict, or list of dicts")
        
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

if __name__ == "__main__":
    client = Clinet()
    while True:
        message = input("You: ")
        if message == "quit":
            break
        response = client.send_message(message)
        print("Assistant: {}".format(response))
