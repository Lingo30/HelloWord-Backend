import os
import openai
from random import shuffle
import requests
import time

from tools.utils import num_tokens_from_messages, completion_with_backoff
from tools.vocabulary import gen_story_from_words, gen_cloze_from_words, gen_example_from_words
from tools.wordlist import gen_wordlist_from_keywords, gen_wordlist_from_passage
from tools.reading import analyze_sentence_in_passage, analyze_sentence_alone
from tools.writing import gen_essay_from_topic, analyze_essay_from_topic, revise_essay_from_topic
openai.api_key = "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" 
temperature = 0
model = "gpt-3.5-turbo-0301"
input = """The natural environment is a precious resource that we must protect and improve for future generations. As individuals, we can make a significant impact on the environment by making conscious choices in our daily lives. While there are many actions we can take to help the environment, one of the most useful actions is to walk or bicycle instead of driving a car to work or school.

Transportation is a significant contributor to greenhouse gas emissions, which are a major cause of climate change. By choosing to walk or bike instead of driving, we can reduce our carbon footprint and help to mitigate the effects of climate change. Additionally, walking or biking is a great way to stay active and improve our physical health.

Recycling and reusing objects is also an important action that individuals can take to help the environment. By recycling, we can reduce the amount of waste that ends up in landfills, which can have harmful effects on the environment. Reusing objects, such as shopping bags or water bottles, can also help to reduce waste and conserve resources.

Buying locally grown, organic foods is another action that individuals can take to help the environment. Locally grown foods require less transportation, which reduces greenhouse gas emissions. Organic farming practices also help to reduce the use of harmful pesticides and chemicals, which can have negative effects on the environment and our health.

While all three actions are important, walking or bicycling instead of driving a car to work or school is the most useful action for individuals to take in their daily lives. This is because transportation is a significant contributor to greenhouse gas emissions, and walking or biking is a simple and effective way to reduce our carbon footprint. Additionally, walking or biking is a great way to stay active and improve our physical health.

In conclusion, protecting and improving the natural environment is a responsibility that we all share. As individuals, we can make a significant impact on the environment by making conscious choices in our daily lives. While there are many actions we can take to help the environment, walking or bicycling instead of driving a car to work or school is the most useful action for individuals to take. By reducing our carbon footprint and improving our physical health, we can help to create a more sustainable future for ourselves and future generations.
"""
input2 = "Many people want to protect and improve the natural environment. Which ONE of the following three actions is MOST useful for individuals to do in their daily lives if they want to help the environment? Why?\n-Walking or bicycling instead of driving a car to work or school\n-Recycling and reusing objects instead of throwing them in the trash (rubbish) can\n-Buying locally grown, organic foods (grown without pesticides)"
tags = ["adventure", "fantasy", "science fiction"]
messages = revise_essay_from_topic(input, input2)
print(messages[0]["content"])
print(f"{num_tokens_from_messages(messages, model)} prompt tokens counted.")
breakpoint()
start = time.perf_counter()
rsp = completion_with_backoff(model=model, messages=messages, temperature=temperature)
end = time.perf_counter()
print(f'request time: {end -start}')
print(rsp['choices'][0]["message"]["content"])