 def __init__(self, audio_file, duration):
        self.audio_file = audio_file
        self.duration = duration
        self.is_recording = False

    def start_recording(self):
        self.is_recording = True
        print("Recording started.")

    def stop_recording(self):
        self.is_recording = False
        print("Recording stopped.")

    def get_audio(self):
        return self.audio_file
