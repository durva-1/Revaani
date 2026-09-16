class SpeechToText:

    def __init__(self):
        self.language = "Gujarati"

    def transcribe(self, audio_file):
        print("Processing audio:", audio_file)
        text = "નમસ્તે, તમે કેમ છો?"
        return text

    def get_language(self):
        return self.language
