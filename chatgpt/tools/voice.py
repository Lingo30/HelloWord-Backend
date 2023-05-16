from TTS.api import TTS

class Voice:
    def __init__(self, languages='en'):
        self.synthetic_voice = TTS(model_name = TTS.list_models()[0], progress_bar=False, gpu=False) 
        
    def speak(self, text):
        self.synthetic_voice.tts_to_file(text=text, file_path='output.wav')
        return 