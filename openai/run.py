import os
import openai
from random import shuffle
import requests
import time

from utils import num_tokens_from_messages, completion_with_backoff
from tools.vocabulary import gen_story_from_words, gen_cloze_from_words, gen_example_from_words
from tools.wordlist import gen_wordlist_from_keywords, gen_wordlist_from_passage

openai.api_key = "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" 
temperature = 0
model = "gpt-3.5-turbo-0301"
input = """WASHINGTON — Senator Dianne Feinstein on Wednesday pushed back on calls for her resignation but asked to step away from the Judiciary Committee indefinitely while recovering from shingles, responding to mounting pressure from Democrats who have publicly vented concerns that she is unable to perform her job.

Ms. Feinstein, an 89-year-old California Democrat, has been away from the Senate since February, when she was diagnosed with the infection. Her absence has become a problem for Senate Democrats, limiting their ability to move forward with judicial nominations. In recent days, as it became clear she was not planning to return after a two-week recess, pressure began to increase for Ms. Feinstein to resign.

On Wednesday night, she said she would not do so, but offered a stopgap solution, saying she would request a temporary replacement on the panel.

“I understand that my absence could delay the important work of the Judiciary Committee,” Ms. Feinstein said in a statement on Wednesday night, after two House Democrats publicly called on her to leave the Senate. “So I’ve asked Leader Schumer to ask the Senate to allow another Democratic senator to temporarily serve until I’m able to resume my committee work.”

In a statement, a spokesman for Senator Chuck Schumer, Democrat of New York and the majority leader, said that Mr. Schumer would make that request of the Senate next week."""
tags = ["adventure", "fantasy", "science fiction"]
messages = gen_wordlist_from_passage(input)
print(messages[0]["content"])
print(f"{num_tokens_from_messages(messages, model)} prompt tokens counted.")
breakpoint()
start = time.perf_counter()
rsp = completion_with_backoff(model=model, messages=messages, temperature=temperature)
end = time.perf_counter()
print(f'request time: {end -start}')
print(rsp['choices'][0]["message"]["content"])