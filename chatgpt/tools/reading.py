
def analyze_sentence_in_passage(passage, sentence):
    """Analyze the sentence in the passage."""
    input_prompt = "As an AI language model specializing in English learning assistance, your task is to analyze the content and structure of a specific sentence within a given English passage, and provide interpretations of both content and structure in Chinese to assist users in understanding complex sentences.\nYour output should also be in JSON format: {“content”: content_interpretation, “structure”: structure_interpretation}\nEnsure that the content_interpretation is a precise translation in Chinese considering the context, while the structure_interpretation provides a detailed analyzation of the syntax structures of the given sentence in Chinese.\n"
    sentence_prompt = "Input passage: " + passage + "\Input sentence: " + sentence
    format_prompt = '\nVery Important!!! Please make sure your output is in JSON format: {"content": content_interpretation, "structure": structure_interpretation}\n'
    messages = [
        {"role": "user", "content": input_prompt + sentence_prompt + format_prompt},
    ]
    return messages

def analyze_sentence_alone(sentence):
    """Analyze the sentence。"""
    input_prompt = "As an AI language model specializing in English learning assistance, your task is to analyze the content and structure of a specific complex sentence, providing interpretations of both content and structure in Chinese to help users understand challenging sentences often encountered in English exams.\nYour output should be in JSON format: {“content”: content_interpretation, “structure”: structure_interpretation}\nEnsure that the content_interpretation is a precise translation in Chinese, while the structure_interpretation offers a detailed analysis of the syntax and sentence structure in Chinese, including a concrete example from the original sentence for each point. Note that the analysis should be in Chinese, while the referring example should be the original text in English. This approach caters to users' needs in the context of English exams.\n"
    sentence_prompt = "Input sentence: " + sentence
    format_prompt = '\nVery Important!!! Please make sure your output is in JSON format: {"content": content_interpretation, "structure": structure_interpretation}\n'
    messages = [
        {"role": "user", "content": input_prompt + sentence_prompt + format_prompt},
    ]
    return messages    
