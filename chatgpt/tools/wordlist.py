# TODO: add difficulty level to the wordlist
# TODO: add a option to select formal or informal words
def gen_wordlist_from_keywords(keywords, num=20):
    input_prompt = 'As an AI language model specializing in English learning assistance, your task is to generate a targeted vocabulary list based on the given keywords and an integer named "word_num". Provide "word_num" relevant English words connected to the given keywords that are essential for learners to understand in specific contexts. The input format is: [keyword1, keyword2, ...]. The output format must be a Python list including resulting words: [word1, word2, ...].\nFor instance, if the input keywords are [academic conference, computer science] and the word_num = 4, the expected output could be [workshop, pipeline, vision, submission].\nNote that the generated words should be useful for English learners and should be frequently used in academic writing, dialogues, or other formal contexts. Each generated word must be a single word that does not contain any spaces!\n'
    words_prompt = "[" + ", ".join(keywords) + "]"
    messages = [
        {"role": "user", "content": input_prompt + "Input keywords: " + words_prompt + "\nInput word_num: " + str(num) + "\nOutput: "},
    ]
    return messages

# TODO: add known words to the wordlist
def gen_wordlist_from_passage(passage, max_num=20, min_num=10):
    input_prompt = f'As an AI language model specializing in English learning assistance, your task is to generate a targeted vocabulary list with size of {min_num}-{max_num} based on a given English paragraph. Identify words in the paragraph that are important and challenging for English learners to understand or are infrequently used. The total number of words should greater than {min_num} and less than {max_num}. Provide your response in a list of words separated by commas in the format of: [word1, word2, ...]. Please focusing on rare, difficult, and essential terms within the paragraph. Each chosen word must be a single word that does not contain spaces!\n'
    words_prompt = passage
    messages = [
        {"role": "user", "content": input_prompt + "Input passage: " + words_prompt + "\nOutput: "},
    ]
    return messages
