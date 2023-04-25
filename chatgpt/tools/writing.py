def gen_essay_from_topic(topic, max_num=500, min_num=400):
    input_prompt = f"As an AI language model, your task is to compose a high-quality English essay of {min_num}-{max_num} words on the provided topic, suitable for exams such as TOEFL or IELTS. Your writing should be clear, concise, and well-organized, with a strong emphasis on the central idea or argument of the passage. Be sure to include relevant details and examples to support your points.\nAdditionally, ensure that your writing adheres to standard conventions of grammar, punctuation, spelling, and sentence structure. You may consult any appropriate sources for research or inspiration but remember to properly cite them if used.\nPlease note that you have creative freedom in addressing the given topic, as long as your approach fulfills the requirements outlined above.\n"
    messages = [
        {"role": "user", "content": input_prompt + "Input topic: " + topic + "\n"},
    ]
    return messages

def analyze_essay(essay, topic=None):
    if topic is None:
        input_prompt = 'As an AI language model, your task is to analyze an English essay, evaluate its content and structure, identify various errors such as grammar, tense, etc., and provide a rating out of ten.\nYour analysis should encompass the overall logical structure, main idea, and specific writing issues such as grammar, punctuation, spelling, and sentence structure, and provide detailed opinions on how to improve the quality of the given essay.\nThe output should be in JSON format: {"analysis": analysis_of_essay, "rating": rating_of_essay}\n'
    else:
        input_prompt = 'As an AI language model, your task is to analyze an English essay on a given topic, evaluate its content and structure, identify various errors such as grammar, tense, etc., and provide a rating out of ten.\nYour analysis should encompass the overall logical structure, main idea, and specific writing issues such as grammar, punctuation, spelling, and sentence structure, and provide detailed opinions on how to improve the quality of the given essay.\nThe output should be in JSON format: {"analysis": analysis_of_essay, "rating": rating_of_essay}\n'
    input_prompt += 'If the input is not a valid essay, please fill all the fields with "None".\n'
    topic_prompt = "\nInput topic: " + topic + "\n" if topic is not None else "\n"
    format_prompt = 'Very Important!!! Please make sure that your output is in JSON format: {"analysis": analysis_of_essay, "rating": rating_of_essay}\nNote that the analysis_of_essay in the "analysis" field should be a string, and the rating_of_essay in the "rating" field should be an integer.\n'
    messages = [
        {"role": "user", "content": input_prompt + "Input essay: " + essay + topic_prompt + format_prompt},
    ]
    return messages

def revise_essay_from_topic(essay, topic):
    input_prompt = 'Your task is to revise and improve an English essay on a given topic, ensuring that it is free of grammar errors and has clear structure. Please provide a revised version that improves the quality while maintaining the original meaning and intent of the essay.\nYour response should demonstrate your ability to write clearly and effectively by providing a well-written and error-free revised version of the essay. In addition to correcting any grammatical errors or awkward phrasing, you should also focus on improving the clarity and coherence of the writing. This may involve reorganizing paragraphs, adding transitional phrases, or clarifying confusing sentences.\nPlease note that while your goal is to improve the quality of the essay, you should strive to maintain its original voice and style, and follow the given topic as much as possible. Your revisions should enhance rather than detract from the author\'s unique perspective and ideas.\n'
    messages = [
        {"role": "user", "content": input_prompt + "Input essay: " + essay + "\nInput topic: " + topic + "\n"},
    ]
    return messages

