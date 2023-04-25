import random

def gen_story_from_words(words, tags=None):
    tags_prompt = "; ".join(tags) if tags else "None"
    input_prompt = 'As an English learning assistant, your task is to write a short story using all the provided input words. The story should be under 200 words, and each input word should be enclosed in "$" characters at both beginning and end.\nInput format: [word1, word2, ...].\nMake sure the story is engaging and interesting, and clearly use the vocabulary in context.'
    if tags:
        input_prompt = input_prompt + ' ' + 'Compose the story within the themes of: ' + tags_prompt + ', and it must include all the provided input words.\n'
    else:
        input_prompt = input_prompt + ' ' + 'You can choose any genre or theme for the story, but it must include all the provided input words.\n'
    input_prompt = input_prompt + "Your response should showcase originality and imagination while seamlessly integrating the input words into a coherent and well-structured narrative.\n"
    words_prompt = "[" + ", ".join(words) + "]" + "INPUT END"
    messages = [
        {"role": "user", "content": input_prompt + "Input words: " + words_prompt},
    ]
    return messages

def gen_cloze_from_words(words, tags=None):
    tags_prompt = "; ".join(tags) if tags else "None"
    input_prompt = 'As an English learning assistant, your task is to create a cloze test that aids users in learning the input words. The input format is: [word1, word2, ...]. Each word should be utilized in the cloze test only once and shoulde be enclosed in the "$" character at both the beginning and end. Please also provide the answer to the cloze test.\nOutput format must be in JSON format: {"content": cloze_test, "answer": [answer1, answer2, ...]}\nProvide your response in JSON format, with two keys: "content" and "answer". The value for "content" should include the cloze test and each used input words should be enclosed in “$”. The value for "answer" should be a list containing answer words for all clozes in sequence.\nRemember to incorporate context clues or hints within the text to assist users with unfamiliar vocabulary. Additionally, ensure your cloze test adheres to proper grammar and sentence structure.'
    if tags:
        input_prompt = input_prompt + ' ' + 'Create the test within the themes of: ' + tags_prompt + ', and it must include all the provided input words.\n'
    else:
        input_prompt = input_prompt + ' ' + 'You can choose any genre or theme for the content of cloze test, but it must include all the provided input words.\n'
    words_prompt = "[" + ", ".join(words) + "]" + "INPUT END\n"
    format_prompt = 'Very Important!!! Your response should be in JSON format: {"content": cloze_test, "answer": [answer1, answer2, ...]}'
    messages = [
        {"role": "user", "content": input_prompt + "Input words: " + words_prompt + format_prompt},
    ]
    return messages

def gen_example_from_words(words, tags=None):
    tags_prompt = random.choice(tags) if tags else "None"
    input_prompt = 'As an AI language model specializing in English learning assistance, your objective is to create a professionally crafted example sentence using all the provided input words. Enclose each input word with "$" characters at the beginning and end. The input format is: [word1, word2, ...]. Note that you have to deal with only one input word in the format of: [word]. Design the sentence to clearly demonstrate the usage and context of each input word, making it easier for the user to memorize and understand their meanings.'
    if tags:
        input_prompt = input_prompt + ' ' + 'Create the example sentence within the themes of: ' + tags_prompt + ', and it must include all the provided input words.\n'
    else:
        input_prompt = input_prompt + ' ' + 'You can choose any genre or theme for the example sentence, but it must include all the provided input words.\n'
    
    words_prompt = "[" + ", ".join(words) + "]" + "INPUT END"
    messages = [
        {"role": "user", "content": input_prompt + "Input words: " + words_prompt},
    ]
    return messages