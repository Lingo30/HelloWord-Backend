import os
import openai
from random import shuffle
import requests
import time

from utils import num_tokens_from_messages, completion_with_backoff
from tools.vocabulary import gen_story_from_words, gen_cloze_from_words, gen_example_from_words
from tools.wordlist import gen_wordlist_from_keywords, gen_wordlist_from_passage
from tools.reading import analyze_sentence_in_passage, analyze_sentence_alone

openai.api_key = "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" 
temperature = 0
model = "gpt-3.5-turbo-0301"
input = "In many instances, spectators in the era before recorded sound experienced elaborate aural presentations alongside movies' visual images, from the Japanese benshi (narrators) crafting multivoiced dialogue narratives to original musical compositions performed by symphony-size orchestras in Europe and the United States."
input2 = "Ms. Feinstein, an 89-year-old California Democrat, has been away from the Senate since February, when she was diagnosed with the infection."
tags = ["adventure", "fantasy", "science fiction"]
messages = analyze_sentence_alone(input)
print(messages[0]["content"])
print(f"{num_tokens_from_messages(messages, model)} prompt tokens counted.")
breakpoint()
start = time.perf_counter()
rsp = completion_with_backoff(model=model, messages=messages, temperature=temperature)
end = time.perf_counter()
print(f'request time: {end -start}')
print(rsp['choices'][0]["message"]["content"])